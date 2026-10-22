import sys, re, pathlib, zipfile

# Static check of mixins against the decompiled sources each repo's build already made: every method, call target and
# accessor a mixin names must still exist under that name, with the same parameter count, and a call a mixin hooks must
# still be made inside the method it targets. Run through `fleet mixins`, or directly:
#   python mixin_check.py <repo dirs...>
# A repo needs a build first, as the sources jars are what NeoForge's and Fabric's dev setup leave under build/moddev.

roots = [pathlib.Path(p) for p in sys.argv[1:]]
sources = {}


def first_jar(root, pattern):
    found = sorted(p for p in root.rglob(pattern) if '/moddev/artifacts/' in p.as_posix())
    return zipfile.ZipFile(found[0]) if found else None


def open_sources(root):
    """The vanilla, NeoForge patched and NeoForge API sources for one repo."""
    vanilla = first_jar(root, 'vanilla-*-sources.jar')
    patched = first_jar(root, 'minecraft-patched-*-sources.jar')
    neoapi = None
    if patched is not None:
        version = re.search(r'minecraft-patched-(.+)-sources\.jar', patched.filename).group(1)
        cache = pathlib.Path.home() / '.gradle/caches/modules-2/files-2.1/net.neoforged/neoforge' / version
        api = sorted(cache.rglob(f'neoforge-{version}-sources.jar')) if cache.exists() else []
        neoapi = zipfile.ZipFile(api[0]) if api else None
    if vanilla is None:
        sys.exit(f'{root}: no vanilla sources jar under build/moddev; build the repo first')
    return {'vanilla': vanilla, 'patched': patched, 'neoapi': neoapi}


def read(jar, rel):
    if jar is None:
        return None
    try:
        return jar.read(rel).decode('utf-8', errors='replace')
    except KeyError:
        return None


def source_for(fqcn, loader):
    rel = fqcn.split('$')[0].replace('.', '/') + '.java'
    order = ['patched', 'neoapi', 'vanilla'] if loader == 'neoforge' else ['vanilla']
    for name in order:
        src = read(sources.get(name), rel)
        if src is not None:
            return src
    return None


def with_supers(fqcn, loader, depth=0):
    """The class's source plus its superclasses' and interfaces', as one text to search."""
    src = source_for(fqcn, loader)
    if src is None or depth > 5:
        return src or ''
    imports = imports_of(src)
    pkg = fqcn.rsplit('.', 1)[0]
    out = [src]
    m = re.search(r'\b(?:class|interface|record|enum)\s+' + re.escape(fqcn.rsplit('.', 1)[1]) + r'\b([^{]*)\{', src)
    if m:
        for sup in re.findall(r'\b([A-Z]\w*(?:\.[A-Z]\w*)*)', re.sub(r'<[^<>]*>', '', re.sub(r'<[^<>]*>', '', m.group(1)))):
            head = sup.split('.')[0]
            fq = imports.get(head, pkg + '.' + head)
            if fq != fqcn:
                out.append(with_supers(fq, loader, depth + 1))
    # BlockState and friends get their members from nested bases declared elsewhere.
    if fqcn.endswith('.BlockState'):
        out.append(with_supers('net.minecraft.world.level.block.state.BlockBehaviour', loader, depth + 1))
    if loader == 'neoforge':
        ext = source_for('net.neoforged.neoforge.common.extensions.I' + fqcn.rsplit('.', 1)[1] + 'Extension', loader)
        if ext:
            out.append(ext)
    return '\n'.join(out)


def desc_params(desc):
    """Number of parameters in a JVM descriptor like (Lfoo;I[J)V."""
    m = re.match(r'\((.*?)\)', desc)
    if not m:
        return None
    s, n, i = m.group(1), 0, 0
    while i < len(s):
        while s[i] == '[':
            i += 1
        if s[i] == 'L':
            i = s.index(';', i) + 1
        else:
            i += 1
        n += 1
    return n


def param_type(p):
    """The simple type of one parameter declaration: 'final Holder<Biome> biome' -> 'Holder'."""
    p = re.sub(r'@[\w.]+(\([^)]*\))?\s*', '', p).replace('final ', '').strip()
    p = re.sub(r'<.*>', '', p)
    parts = p.split()
    t = parts[0] if parts else ''
    return t.split('.')[-1].replace('...', '[]')


def declared_param_types(src, name):
    out = []
    for m in re.finditer(r'(?<![\w.])' + re.escape(name) + r'\s*\(', src):
        before = src[max(0, m.start() - 120):m.start()]
        if not re.search(r'[\w>\]]\s+$', before) or re.search(r'(return|new|\.|=|\()\s*$', before):
            continue
        depth, j, start = 0, m.end() - 1, m.end()
        params = []
        while j < len(src):
            c = src[j]
            if c in '(<':
                depth += 1
            elif c in ')>':
                depth -= 1
                if depth == 0 and c == ')':
                    params.append(src[start:j])
                    break
            elif c == ',' and depth == 1:
                params.append(src[start:j])
                start = j + 1
            j += 1
        tail = src[j + 1:j + 200].lstrip()
        if not (tail.startswith('{') or tail.startswith('throws') or tail.startswith(';')):
            continue
        out.append([] if len(params) == 1 and not params[0].strip() else [param_type(x) for x in params])
    return out


def declared_param_counts(src, name):
    counts = set()
    for m in re.finditer(r'(?<![\w.])' + re.escape(name) + r'\s*\(', src):
        # Skip calls: a declaration has a type or modifier right before the name.
        before = src[max(0, m.start() - 120):m.start()]
        if not re.search(r'[\w>\]]\s+$', before) or re.search(r'(return|new|\.|=|\()\s*$', before):
            continue
        depth, j, start = 0, m.end() - 1, m.end()
        params = []
        while j < len(src):
            c = src[j]
            if c in '(<':
                depth += 1
            elif c in ')>':
                depth -= 1
                if depth == 0 and c == ')':
                    params.append(src[start:j])
                    break
            elif c == ',' and depth == 1:
                params.append(src[start:j])
                start = j + 1
            j += 1
        tail = src[j + 1:j + 200].lstrip()
        if not (tail.startswith('{') or tail.startswith('throws') or tail.startswith(';')):
            continue
        counts.add(0 if len(params) == 1 and not params[0].strip() else len(params))
    return counts


def imports_of(src):
    imp = {}
    for m in re.finditer(r'(?m)^import\s+([\w.]+)\.(\w+)\s*;', src):
        imp[m.group(2)] = m.group(1) + '.' + m.group(2)
    return imp


INJECTOR = re.compile(r'@(?:Inject|Redirect|ModifyVariable|ModifyArg|ModifyArgs|ModifyConstant|ModifyExpressionValue|'
                      r'ModifyReturnValue|WrapOperation|WrapWithCondition)\s*\(')


def balanced(src, start, open_c='(', close_c=')'):
    """The text between the bracket at start and its match, stepping over string literals."""
    depth, j = 0, start
    while j < len(src):
        c = src[j]
        if c == '"':
            j = src.index('"', j + 1)
        elif c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return src[start + 1:j]
        j += 1
    return ''


def method_bodies(src, name):
    """The body of every declaration of name in src."""
    bodies = []
    for m in re.finditer(r'(?<![\w.])' + re.escape(name) + r'\s*\(', src):
        before = src[max(0, m.start() - 120):m.start()]
        if not re.search(r'[\w>\]]\s+$', before) or re.search(r'(return|new|\.|=|\()\s*$', before):
            continue
        params = balanced(src, m.end() - 1)
        after = m.end() - 1 + len(params) + 2
        brace = re.match(r'\s*(?:throws[^{;]*)?\{', src[after:])
        if brace:
            bodies.append(balanced(src, after + brace.end() - 1, '{', '}'))
    return bodies


problems = 0
for root in roots:
    sources = open_sources(root)
    for p in root.rglob('*.java'):
        if '/build/' in p.as_posix() or '/bin/' in p.as_posix():
            continue
        src = p.read_text(encoding='utf-8', errors='replace')
        mm = re.search(r'@Mixin\(\s*(?:value\s*=\s*)?\{?\s*([\w.]+)\.class', src)
        if not mm:
            continue
        loader = 'neoforge' if '/neoforge/' in p.as_posix() else ('fabric' if '/fabric/' in p.as_posix() else 'common')
        target_simple = mm.group(1)
        imports = imports_of(src)
        head = target_simple.split('.')[0]
        if head in imports:
            fq = imports[head] + target_simple[len(head):]
        else:
            fq = target_simple
        # Nested classes: Outer.Inner -> file of Outer
        parts = fq.split('.')
        outer_idx = next((i for i, x in enumerate(parts) if x[:1].isupper()), len(parts) - 1)
        fq_file = '.'.join(parts[:outer_idx + 1])
        tsrc = with_supers(fq_file, loader) or None
        name = p.relative_to(root).as_posix().split('/java/')[-1]
        if tsrc is None:
            if not fq.startswith('net.minecraft') and not fq.startswith('com.mojang'):
                continue
            print(f'{root.name}: {name}: target {fq} has no source')
            problems += 1
            continue

        def report(msg):
            global problems
            problems += 1
            print(f'{root.name}: {name}: {msg}')

        for m in re.finditer(r'\bmethod\s*=\s*(\{[^}]*\}|"[^"]*")', src):
            for sel in re.findall(r'"([^"]+)"', m.group(1)):
                mname = re.split(r'[(*]', sel)[0]
                if mname in ('<init>', '<clinit>') or mname.startswith('lambda$'):
                    if mname.startswith('lambda$'):
                        print(f'{root.name}: {name}: note, lambda target {sel} cannot be checked')
                    continue
                counts = declared_param_counts(tsrc, mname)
                if not counts:
                    report(f'method {sel} not found in {fq}')
                    continue
                n = desc_params(sel[len(mname):]) if '(' in sel else None
                if n is not None and n not in counts:
                    report(f'method {sel}: {fq}.{mname} takes {sorted(counts)} parameters now')
        # An @Inject handler takes the target's parameters, then its CallbackInfo.
        for m in re.finditer(r'@Inject\((?:[^()]|\([^()]*(?:\([^()]*\)[^()]*)*\))*\)\s*(?:@\w+(?:\([^)]*\))?\s*)*'
                             r'(?:(?:private|protected|public|static|final)\s+)*[\w<>\[\], ?]+\s+\w+\s*\(([^)]*)\)', src):
            sel = re.search(r'\bmethod\s*=\s*\{?\s*"([^"]+)"', m.group(0))
            if not sel:
                continue
            mname = re.split(r'[(*]', sel.group(1))[0]
            if mname.startswith('lambda$') or mname in ('<init>', '<clinit>'):
                continue
            handler = [param_type(x) for x in m.group(1).split(',') if x.strip()]
            cut = next((i for i, t in enumerate(handler) if t.startswith('CallbackInfo')), None)
            if cut is None:
                continue
            handler = handler[:cut]
            overloads = declared_param_types(tsrc, mname)
            if overloads and handler and not any(o == handler for o in overloads):
                report(f'@Inject {mname} handler takes {handler}; {fq}.{mname} takes {overloads}')
        for m in re.finditer(r'\btarget\s*=\s*"L([\w/$]+);([\w<>$]+)(\([^"]*\))?[^"]*"', src):
            owner = m.group(1).replace('/', '.')
            mname = m.group(2)
            if mname in ('<init>',):
                continue
            # Owners outside the decompiled sources, such as DataFixerUpper's Codec, cannot be checked.
            if source_for(owner, loader) is None:
                continue
            osrc = with_supers(owner.split('$')[0], loader)
            counts = declared_param_counts(osrc, mname)
            if not counts and not re.search(r'\b' + re.escape(mname) + r'\b', osrc):
                report(f'call target {owner}.{mname} not found')
                continue
            if m.group(3) and counts:
                n = desc_params(m.group(3))
                if n not in counts:
                    report(f'call target {owner}.{mname}{m.group(3)} takes {sorted(counts)} parameters now')
        # A hooked call that moved elsewhere, as 26.3's mining hit sound did, otherwise only shows as a crash at world load.
        for m in INJECTOR.finditer(src):
            args = balanced(src, m.end() - 1)
            selectors = re.search(r'\bmethod\s*=\s*(\{[^}]*\}|"[^"]*")', args)
            if not selectors:
                continue
            calls = []
            for at in re.finditer(r'@At\s*\(', args):
                at_args = balanced(args, at.end() - 1)
                if re.search(r'"INVOKE(?:_ASSIGN)?"', at_args):
                    target = re.search(r'\btarget\s*=\s*"L[\w/$]+;([\w$]+)\(', at_args)
                    if target:
                        calls.append(target.group(1))
            for sel in re.findall(r'"([^"]+)"', selectors.group(1)):
                mname = re.split(r'[(*]', sel)[0]
                if mname.startswith('lambda$') or mname in ('<init>', '<clinit>'):
                    continue
                bodies = method_bodies(tsrc, mname)
                for call in calls:
                    if bodies and not any(re.search(r'(?<![\w$])' + re.escape(call) + r'\s*\(|::' + re.escape(call) + r'\b', b) for b in bodies):
                        report(f'{fq}.{mname} no longer calls {call}, which a hook here targets')
        for m in re.finditer(r'@(Accessor|Invoker)\(\s*(?:value\s*=\s*)?"([^"]+)"', src):
            kind, member = m.groups()
            if not re.search(r'\b' + re.escape(member) + r'\b', tsrc):
                report(f'{kind} {member} not found in {fq}')
        for m in re.finditer(r'@(Accessor|Invoker)\s*\n\s*[\w<>\[\], ?]+\s+(\w+)\(', src):
            kind, meth = m.groups()
            member = re.sub(r'^(get|set|is|invoke|call)', '', meth)
            # A constant keeps its capitals: getMOBS reads MOBS.
            if not re.fullmatch(r'[A-Z0-9_]+', member):
                member = member[:1].lower() + member[1:]
            if member and not re.search(r'\b' + re.escape(member) + r'\b', tsrc):
                report(f'{kind} {meth} (member {member}) not found in {fq}')
        for m in re.finditer(r'@Shadow[^\n]*\n\s*(?:@\w+\s*)*(?:(?:private|protected|public|static|final|abstract)\s+)*[\w<>\[\], ?.]+\s+(\w+)\s*[;(]', src):
            member = m.group(1)
            if not re.search(r'\b' + re.escape(member) + r'\b', tsrc):
                report(f'@Shadow {member} not found in {fq}')
print(f'== {problems} problems', file=sys.stderr)
sys.exit(1 if problems else 0)
