inutili = ['il', 'lo', 'la', 'i', 'gli', 'le', 'l', 'un', 'uno', 'una', 'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra',
           'fra', 'del', 'della', 'degli', 'dello', 'delle', 'al', 'allo', 'alla', 'agli', 'ai', 'alle', 'dal', 'dalla',
           'dallo', 'dalle', 'dagli', 'dai', 'nel', 'nello', 'nella', 'nelle', 'negli', 'nei', 'sul', 'sui', 'sulla',
           'sulle', 'sullo', 'quale', 'quali', 'quando', 'quale', 'all', 'dell', 'nell', 'dall', 'sull', 'quell', 'qual'
           'questo', 'questa', 'questi', 'queste', 'quest', 'chi', 'che', 'si', 'loro', 'non', 'e', 'che', 'è', 'ha', 'più',
           '|']
chiave = ['non', 'falso', 'falsa', 'nord', 'sud', 'ovest', 'est']
chiave_regole = []

banned_words = set(word for word in inutili)