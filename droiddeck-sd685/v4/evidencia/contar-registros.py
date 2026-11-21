"""Counts the evidence in an unpacked DroidDeck diagnostics ZIP (steam session folder given as argv[1])."""
import hashlib, os, re, sys
d = sys.argv[1]
names = ['webhelper.txt', 'steamui_html.txt', 'console-linux.txt', 'webhelper_gpu.txt', 'bootstrap_log.txt']
files = {}
for n in names:
    e = os.path.join(d, 'steam', 'entry-%s.txt' % hashlib.sha256(n.encode()).hexdigest()[:16])
    files[n] = e if os.path.isfile(e) else os.path.join(d, 'steam', n)
    print('%-20s <- %s' % (n, os.path.relpath(files[n], d)))
def count(name, pattern):
    with open(files[name], errors='replace') as f:
        return sum(1 for line in f if pattern in line)
print()
for name, pattern in [
        ('webhelper.txt', 'CCompositorGLThread::CreateOutputWindow'),
        ('webhelper.txt', 'failed to acquire a gl context'),
        ('webhelper.txt', 'Falling back to system composer'),
        ('steamui_html.txt', 'Restart webhelper process'),
        ('console-linux.txt', 'GPU process exited unexpectedly'),
        ('console-linux.txt', "GPU process isn't usable"),
        ('console-linux.txt', 'failed to create dri3 screen'),
        ('console-linux.txt', 'failed to load driver: zink'),
        ('console-linux.txt', 'failed to load driver: swrast'),
        ('console-linux.txt', 'ZINK: vkCreateInstance failed'),
        ('console-linux.txt', 'vkEnumeratePhysicalDevices failed'),
        ('webhelper_gpu.txt', 'GL implementation parts ]: (gl=none,angle=none)'),
        ('webhelper_gpu.txt', 'GL_RENDERER ]: (null)')]:
    print('%5d  %-18s %s' % (count(name, pattern), name, pattern))
w = open(os.path.join(d, 'wayland.log'), errors='replace').read()
pacing = re.findall(r'\((\d+) scenes.*?\| (\d+) game frames.*?(\d+) distinct buffers', w)
print('\nwayland.log: %d ten-second reports; scenes, game frames, distinct buffers: %s' % (
    len(pacing), sorted(set(pacing))))
print('wayland.log GPU: %s' % '; '.join(re.findall(r'compositor renders on ([^\n]+)', w)))
launcher = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f == 'entry-%s.log' % hashlib.sha256(b'steam-x64.log').hexdigest()[:16]]
for path in launcher:
    text = open(path, errors='replace').read()
    print('\nsteam-x64.log: "steam is still starting" lines (v3 watch alive): %d' % text.count('steam is still starting'))
    for line in re.findall(r'.*repairing the x86-64 Steam client.*', text):
        print('steam-x64.log: ' + line.strip())
s = open(os.path.join(d, 'session.log'), errors='replace').read()
for line in re.findall(r'.*(?:droiddeck-proton-armv80|Proton for ARMv8.0|for ARMv8.0: rewriting).*', s):
    print('session.log: ' + line.strip()[:200])
