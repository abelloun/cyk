from CCGrammar import CCGrammar
from CCGCKYParser import CCGCKYParser

grammar = '''

    :- Phrase, GrNom, Nom
    :- VerbeInf, PhraseInterro, GrQuestion, Prop, PP

    DetMasc :: GrNom[Masc]/Nom[Masc]
    DetFem :: GrNom[Fem]/Nom[Fem]
    DetMascPlur :: GrNom[MascPlur]/Nom[MascPlur]
    DetFemPlur :: GrNom[FemPlur]/Nom[FemPlur]

    AdjMascL :: Nom[Masc]/Nom[Masc]
    AdjFemL :: Nom[Fem]/Nom[Fem]
    AdjMascR :: Nom[Masc]\\Nom[Masc]
    AdjFemR :: Nom[Fem]\\Nom[Fem]
    VbIntransM :: Phrase\\GrNom[Masc]
    VbIntransF :: Phrase\\GrNom[Fem]
    VbTransM :: VbIntransM/GrNom
    VbTransF :: VbIntransF/GrNom
    AnteposMasc :: VbIntransM/VbTransM
    AnteposFem :: VbIntransF/VbTransF
    AdvM :: VbIntransM\\VbIntransM
    AdvF :: VbIntransF\\VbIntransF
    AdvTM :: VbTransM\\VbTransM
    AdvTF :: VbTransF\\VbTransF

    chat =>(1) Nom[Masc] {\\x. chat(x)}
    fromage => Nom[Masc] {\\x. fromage(x)}
    rat => Nom[Masc] {\\x. rat(x)}
    voisin => Nom[Masc] {\\x. voisin(x)}
    sœur => Nom[Fem] {\\x. soeur(x)}
    souris => Nom[Fem] {\\x. souris(x)}
    souris => Nom[FemPlur] {\\x. souris(x)}
    dents => Nom[FemPlur] {\\x. dents(x)}

    la => DetFem {\\P. P}
    le => DetMasc  {\\P. P}
    La => DetFem  {\\P. P}
    Le => DetMasc   {\\P. P}
    ma => DetFem  {\\P. P}
    mon => DetMasc  {\\P. P}
    mes => DetMasc  {\\P. P}
    mes => DetFem  {\\P. P}
    ses => DetMascPlur  {\\P. P}
    ses => DetFemPlur  {\\P. P}
    un =>(1) DetMasc   {\\P. P}
    Un =>(1) DetMasc   {\\P. P}

    la => AnteposMasc {\\P. P(feminin)}
    le => AnteposMasc {\\P. P(masculin)}
    la => AnteposFem {\\P. P(feminin)}
    le => AnteposFem {\\P. P(masculin)}

    méchant => AdjMascL {\\P z. (P(z) & méchant(z))}
    noir => AdjMascR {\\P z. (P(z) & noir(z))}
    donné => PP[Masc] {\\x y z. donner(x, y, z)}
    mangée => PP[Fem] {\\P x y. (P(y) & manger(x, y))}

    très => AdjMascL/AdjMascL {\\P. P}
    très => AdjFemL/AdjFemL {\\P. P}
    très => AdjMascR/AdjMascR {\\P. P}
    très => AdjFemR/AdjFemR {\\P. P}

    Il => Phrase/VbIntransM {\\P. P(masculin)}
    Elle => Phrase/VbIntransF {\\P. P(feminin)}

    pourchasse => VbTransF {\\P Q y x. (P(x) & Q(y) & pourchasser(y, x))}
    pourchasse => VbTransM {\\P Q y x. (P(x) & Q(y) & pourchasser(y, x))}
    attrape => VbTransF {\\P Q y x. (P(x) & Q(y) & attraper(y, x))}
    attrape => VbTransM {\\P Q y x. (P(x) & Q(y) & attraper(y, x))}
    mange => VbTransF {\\P Q y x. (P(x) & Q(y) & manger(y, x))}
    mange => VbTransM {\\P Q y x. (P(x) & Q(y) & manger(y, x))}
    ##mange => VbIntransM {\\x. manger(x)}
    ##mange => VbIntransF {\\x. manger(x)}
    dorment => Phrase\\GrNom[MascPlur] {\\P x. (P(x) & dormir(x))}
    dorment => Phrase\\GrNom[FemPlur] {\\P x. (P(x) & dormir(x))}
    dort => VbIntransM {\\P x. (P(x) & dormir(x))}
    dort => VbIntransF {\\P x. (P(x) & dormir(x))}
    donne => VbTransM {\\P Q S y x z. (P(x) & Q(y) & S(z) & donner(z, x, y))}
    donne => VbTransF {\\P Q S y x z. (P(x) & Q(y) & S(z) & donner(z, x, y))}
    souhaite => VbTransM/VerbeInf {souhaite}
    souhaite => VbTransF/VerbeInf {souhaite}
    souhaite => VbIntransM/Prop {souhaite}
    souhaite => VbIntransF/Prop {souhaite}

    est => VbIntransF/AdjFemR {\\P. P}
    est => VbIntransM/AdjMascL {\\P. P}
    est => VbIntransF/AdjFemL {\\P. P}
    est => VbIntransM/AdjMascR {\\P. P}
    est => VbIntransF/PP[Fem] {\\P. P}
    est => VbIntransM/PP[Masc] {\\P. P}

    #a => VbIntransF/PP[Fem] {est}
    #a => VbIntransM/PP[Masc] {est}

    donner => VerbeInf {donner}

    paisiblement => AdvM {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvF {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvTM {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvTF {\\P R z. (P(R, z) & paisible(z))}

    à => (VbIntransM\\VbIntransM)/GrNom {\\P Q x. Q(P, x)}
    à => (VbIntransF\\VbIntransF)/GrNom {\\P Q x. Q(P, x)}
    à => (PP[Masc]\\PP[Masc])/GrNom {\\P Q x. Q(P, x)}
    #à => (PP[Fem]\\PP[Fem])/GrNom {à}
    #à => (VbTransM\\AnteposMasc)\\VbTransM {à}
    #à => (VbTransF\\AnteposFem)\\VbTransF {à}
    A => (PhraseInterro/Phrase)/(PhraseInterro/(Phrase\\GrNom)) {à}

    #avec => (VbIntransM\\VbIntransM)/GrNom[Plur]  {avec}
    avec => (VbIntransM\\VbIntransM)/GrNom {\\P Q S x y z. (P(x) & Q(S, z, y) & utilise(z, x))}
    Avec => (PhraseInterro/Phrase)/GrQuestion {\\P Q x y. (exists z. (Q(P(x), y) & utilise(x, z)))}
    de => (GrNom[Masc]\\GrNom[Masc])/GrNom {\\P R x y. (P(y) & R(x) & possede(y, x))}
    de => (GrNom[Fem]\\GrNom[Fem])/GrNom {\\P R x y. (P(y) & R(x) & possede(y, x))}

    et => (GrNom[MascPlur]/GrNom[Fem])\\GrNom[Masc] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[FemPlur]/GrNom[Fem])\\GrNom[Fem] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Masc] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Fem] {\\P Q z. (P(z) & Q (z))}
    et => (VbTransM/VbTransM)\\VbTransM {\\P Q z. (P(z) & Q (z))}
    et => (VbTransF/VbTransF)\\VbTransF {\\P Q z. (P(z) & Q (z))}
    et => (VbIntransF/VbIntransF)\\VbIntransF {\\P Q z. (P(z) & Q (z))}
    et => (VbIntransM/VbIntransM)\\VbIntransM {\\P Q z. (P(z) & Q (z))}
    et => (AdjFemL/AdjFemL)\\AdjFemL {\\P Q z. (P(z) & Q (z))}
    et => (AdjFemR/AdjFemR)\\AdjFemR {\\P Q z. (P(z) & Q (z))}
    et => (AdjMascL/AdjMascL)\\AdjMascL {\\P Q z. (P(z) & Q (z))}
    et => (AdjMascR/AdjMascR)\\AdjMascR {\\P Q z. (P(z) & Q (z))}
    et => (Phrase/Phrase)\\Phrase {\\P Q z. (P(z) & Q (z))}

    lui => ((Phrase/GrNom[Masc])/VbTransM)\\AnteposMasc {\\P. P}
    lui => ((Phrase/GrNom[Fem])/VbTransF)\\AnteposFem {\\P. P}
    lui => ((Phrase/GrNom)/VbTransM)\\GrNom {\\P. P}
    lui => ((Phrase/GrNom)/VbTransF)\\GrNom {\\P. P}

    par => (PP[Masc]\\PP[Masc])/GrNom {\\P Q R x y. (P(x) & Q(R, x, y))}
    par => (PP[Fem]\PP[Fem])/GrNom {\\P Q R x y. (P(x) & Q(R, x, y))}

    que => Prop/Phrase {\\P Q x. P(x) & Q(x)}
    Quel => (PhraseInterro/VbIntransM)/Nom[Masc] {\\P R y.(exists x. (R(P, y, x)))}
    #quel => (PhraseInterro/VbIntransM)/Nom[Masc] {quel}
    Quelle => (PhraseInterro/VbIntransF)/Nom[Fem] {\\P R y.(exists x. (R(P, y, x)))}
    quelle => (PhraseInterro/VbIntransF)/Nom[Fem] {quel}
    qui => (GrNom[Fem]\\GrNom[Fem])/VbIntransF {\\P. P}
    qui => (GrNom[Masc]\\GrNom[Masc])/VbIntransM {\\P. P}
    qui => (GrNom[FemPlur]\\GrNom[FemPlur])/(Phrase\\GrNom[FemPlur]) {\\P. P}
    qui => (GrNom[MascPlur]\\GrNom[MascPlur])/(Phrase\\GrNom[MascPlur]) {\\P. P}
    Qui => (PhraseInterro/(Phrase\\GrNom[Masc])) {\\P x y. P(humain, x, y)}
    Qui => (PhraseInterro/(Phrase\\GrNom[Fem])) {\\x y z w. (z w) & (y (x w))}
    quoi => GrQuestion {\\P. P}

    ? => Phrase\\PhraseInterro {\\P.P}


'''

txt = '''
    Un chat dort
    Il dort
    Le chat dort paisiblement
    Le chat noir dort
    Le méchant chat dort
    Le très méchant chat dort
    Le chat de la sœur de mon voisin dort
    Le chat que mon voisin lui donne mange
    Le chat qui dort est noir
    Le chat mange la souris
    Le chat la mange
    Il la mange
    Quel chat mange la souris ?
    Qui mange la souris ?
    Quelle souris mange le chat ?
    La souris est mangée par le chat
    Elle est mangée par le chat
    Quelle souris est mangée par le chat ?
    Le chat mange la souris avec ses dents
    Le chat la mange avec ses dents
    Avec quoi le chat mange la souris ?
    Le rat donne un fromage à la souris
    Un fromage est donné par le rat à la souris
    A quelle souris un fromage est donné par le rat ?
    Il le donne à la souris
    Il le lui donne
    Il souhaite que mon voisin lui donne le chat
    Il souhaite donner le chat à mon voisin
    Le chat de mon voisin pourchasse et attrape la souris
    La souris dort et le chat de mon voisin attrape la souris
    Le chat dort et la souris dort
    Le chat et la souris dorment

    le chat mange la souris et le fromage
    la souris de mon chat et le fromage dorment
    un fromage très méchant mange le fromage
    le voisin de mon chat mange mon voisin
    Le chat mange mon fromage avec la souris
    Le méchant chat attrape et mange la souris paisiblement
    Le chat est méchant
    La souris est mangée par mon voisin avec ses dents
    Le fromage mange avec ses souris
    Le méchant chat noir est noir et méchant
    Le rat mange ses dents avec ses dents
    La souris est mangée
    La souris est mangée par ses dents
    La souris mange un rat paisiblement
    La souris mange paisiblement paisiblement un rat
'''

txt_test='''
    Un chat dort
    Il dort
    Le chat dort paisiblement
    Le chat noir dort
    Le méchant chat dort
    Le très méchant chat dort
    Le chat de la sœur de mon voisin dort
    Le chat que mon voisin lui donne mange
    Le chat qui dort est noir
    Le chat mange la souris
    Le chat la mange
    Il la mange
    Quel chat mange la souris ?
    Qui mange la souris ?
    Quelle souris mange le chat ?
    La souris est mangée par le chat
    Elle est mangée par le chat
    Quelle souris est mangée par le chat ?
    Le chat mange la souris avec ses dents
    Le chat la mange avec ses dents
    Avec quoi le chat mange la souris ?
    Le rat donne un fromage à la souris
    Un fromage est donné par le rat à la souris
'''


def run(txt):
    ccg = CCGrammar(grammar)
    #~ print(ccg.show())
    for str in [str1 for str in txt.split("\n") for str1 in [str.strip()] if str1]:
        print("##########################################################################################")
        print(f"# Parsing de : \"{str}\" :")
        print("##########################################################################################\n")
        parses = CCGCKYParser(ccg, str)
        if parses:
            for p in parses:
                print(p.show())
                #~ ps = [p]
                #~ q = []
                #~ while ps:
                    #~ p = ps[0]
                    #~ ps = ps[1:]
                    #~ q.append(p)
                    #~ print(p.show())
                    #~ if p.derivation:
                        #~ combinator, sigma, judgs = p.derivation
                        #~ ps = ps + judgs
                #~ q.reverse()
                #~ print("\n".join([qq.show() for qq in q]))
                #~ print("")
            print("\n\n\n\n\n")
        else:
            print(f"@@@@@@@@@@@@ ECHEC on ::: {str} @@@@@@@@@@@@\n")



txt0 = '''
    Un chat dort
'''

run(txt)
run(txt_test)

