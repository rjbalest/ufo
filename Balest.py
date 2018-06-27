import string

# Turn a name into upper camel case.
def UCCNAME(name):
    ucname = string.capwords( name, '_' )
    ucname = string.replace( ucname, '_', '')
    return ucname

def Store(name, hash, lang='python'):
    if lang == 'php':
        return StorePHP(name,hash)

    # Else assume python
    import cPickle
    of = open(name, 'w')
    pickler = cPickle.Pickler(of)
    pickler.dump(hash)
    print "Stored components to %s" % name
    of.close()

def Load(name, lang='python'):
    if lang == 'php':
        return LoadPHP(name)
    
    # Else assume python
    import cPickle
    of = open(name, 'r')
    pickler = cPickle.Unpickler(of)
    hash = pickler.load()
    of.close()
    return hash

# Serialize in PHP serialization format
def StorePHP(name, hash):
    from PHPSerialize import PHPSerialize
    pickler = PHPSerialize.PHPSerialize()
    serialized_str = pickler.serialize(hash)
    
    of = open(name, 'w')
    # write the output to file
    of.write('%s\n' % serialized_str)
    print "Stored components to %s" % name
    of.close()

# Unserialize from PHP serialization format
def LoadPHP(name):
    from PHPSerialize import PHPUnserialize
    pickler = PHPUnserialize.PHPUnserialize()

    of = open(name, 'r')
    serialized_str = ''
    for line in of.readlines():
        serialized_str = serialized_str + line
    of.close()

    hash = pickler.unserialize(serialized_str)
    return hash
