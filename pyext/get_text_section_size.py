﻿import subprocess
import re
import os
import sys
import tempfile

DUMPBIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dumpbin-vs2008.cmd')

def main(objPath, headerTarget, defineName):
    handle, tempPath = tempfile.mkstemp('.dump-out')
    os.close(handle)

    try:
        proc = subprocess.Popen([DUMPBIN, '/section:.text', '/out:%s' % tempPath, objPath],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = proc.communicate()
        if proc.returncode != 0:
            sys.exit('dumpbin errored out:\n%s' % out)
        with open(tempPath) as inp:
            out = inp.read()
    finally:
        os.remove(tempPath)
    
    found = re.findall(r'^\s*([0-9a-fA-F]+)\s*size of raw data\s*$', out, re.MULTILINE)

    try:
        sectionSize = int(found[0])
    except (ValueError, IndexError) as ex:
        sys.exit('dumpbin gave bad output (error: %r):\n%s' % (ex, out))

    contents = '\n'.join(['// Generated by %s from %s' % (sys.argv[0], objPath),
                          '#define %s %s' % (defineName, hex(sectionSize)),
                          ''])
    try:
        with open(headerTarget, 'r') as header:
            old_contents = header.read()
    except IOError:
        pass
    else:
        if contents == old_contents:
            print('%s is already up-to-date' % headerTarget)
            return
    with open(headerTarget, 'w') as header:
        header.write(contents)

if __name__ == '__main__':
    try:
        (objPath, headerTarget, defineName) = sys.argv[1:]
    except ValueError:
        sys.exit('Usage: %s obj-to-get-.text-from header-to-make.h DEFINE_NAME' % sys.argv[0])
    main(objPath, headerTarget, defineName)