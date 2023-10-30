from CCGrammar import CCGrammar
from CCGCKYParser import CCGCKYParser, CKYDerivation
import time

grammar = '''
    :- Phrase, GrNom, Nom
    :- VerbeInf, PhraseInterro, PP

    # Déterminants
    DetMasc :: GrNom[Masc]/Nom[Masc]
    DetFem :: GrNom[Fem]/Nom[Fem]
    DetMascPlur :: GrNom[MascPlur]/Nom[MascPlur]
    DetFemPlur :: GrNom[FemPlur]/Nom[FemPlur]

    # Adjectifs
    AdjMascL :: Nom[Masc]/Nom[Masc]
    AdjFemL :: Nom[Fem]/Nom[Fem]
    AdjMascR :: Nom[Masc]\\Nom[Masc]
    AdjFemR :: Nom[Fem]\\Nom[Fem]
    AdjMascPL :: Nom[MascPlur]/Nom[MascPlur]
    AdjFemPL :: Nom[FemPlur]/Nom[FemPlur]
    AdjMascPR :: Nom[MascPlur]\\Nom[MascPlur]
    AdjFemPR :: Nom[FemPlur]\\Nom[FemPlur]

    # Verbes
    VbIntransSM :: Phrase\\GrNom[Masc]
    VbIntransSF :: Phrase\\GrNom[Fem]
    VbTransSM :: VbIntransSM/GrNom
    VbTransSF :: VbIntransSF/GrNom
    VbIntransPM :: Phrase\\GrNom[MascPlur]
    VbIntransPF :: Phrase\\GrNom[FemPlur]
    VbTransPM :: VbIntransPM/GrNom
    VbTransPF :: VbIntransPF/GrNom

    # Extras
    AnteposMasc :: VbIntransSM/VbTransSM
    AnteposFem :: VbIntransSF/VbTransSF
    AdvM :: VbIntransSM\\VbIntransSM
    AdvF :: VbIntransSF\\VbIntransSF
    AdvTM :: VbTransSM\\VbTransSM
    AdvTF :: VbTransSF\\VbTransSF

    #############################
    #  Reconnaissance des mots  #
    #############################
    # Noms
    chat => Nom[Masc] {\\x. chat(x)}
    fromage => Nom[Masc] {\\x. fromage(x)}
    rat => Nom[Masc] {\\x. rat(x)}
    voisin => Nom[Masc] {\\x. voisin(x)}
    sœur => Nom[Fem] {\\x. soeur(x)}
    souris => Nom[Fem] {\\x. souris(x)}
    souris => Nom[FemPlur] {\\x. souris(x)}
    dents => Nom[FemPlur] {\\x. dents(x)}

    # Déterminants
    la => DetFem {\\P. P}
    le => DetMasc  {\\P. P}
    La => DetFem  {\\P. P}
    Le => DetMasc   {\\P. P}
    ma => DetFem  {\\P. P}
    mon => DetMasc  {\\P. P}
    mes => DetMascPlur  {\\P. P}
    mes => DetFemPlur  {\\P. P}
    ses => DetMascPlur  {\\P. P}
    ses => DetFemPlur  {\\P. P}
    un => DetMasc   {\\P. P}
    Un => DetMasc   {\\P. P}

    # Antépositions
    la => AnteposMasc {\\P. P(feminin)}
    le => AnteposMasc {\\P. P(masculin)}
    la => AnteposFem {\\P. P(feminin)}
    le => AnteposFem {\\P. P(masculin)}
    lui => AnteposMasc\\AnteposMasc {\\P. P} # Antéposition secondaire
    lui => AnteposFem\\AnteposFem {\\P. P}
    lui => ((Phrase/GrNom)/VbTransSM)\\GrNom {\\P. P}
    lui => ((Phrase/GrNom)/VbTransSF)\\GrNom {\\P. P}

    # Adjectifs
    méchant => AdjMascL {\\P z. (P(z) & méchant(z))}
    méchant => AdjMascR {\\P z. (P(z) & méchant(z))}
    noir => AdjMascR {\\P z. (P(z) & noir(z))}
    qui => AdjFemR/VbIntransSF {\\P. P}
    qui => AdjMascR/VbIntransSM {\\P. P}
    qui => AdjFemPR/VbIntransPF {\\P. P}
    qui => AdjMascPR/VbIntransPM {\\P. P}

    # Superlatif
    très => AdjMascL/AdjMascL {\\P. P}
    très => AdjFemL/AdjFemL {\\P. P}
    très => AdjMascR/AdjMascR {\\P. P}
    très => AdjFemR/AdjFemR {\\P. P}

    # Pronoms personnels
    Il => Phrase/VbIntransSM {\\P. P(masculin)}
    Elle => Phrase/VbIntransSF {\\P. P(feminin)}

    # Verbes
    pourchasse => VbTransSF {\\P Q y x. (P(x) & Q(y) & pourchasser(y, x))}
    pourchasse => VbTransSM {\\P Q y x. (P(x) & Q(y) & pourchasser(y, x))}
    attrape => VbTransSF {\\P Q y x. (P(x) & Q(y) & attraper(y, x))}
    attrape => VbTransSM {\\P Q y x. (P(x) & Q(y) & attraper(y, x))}
    mange => VbTransSF {\\P Q y x. (P(x) & Q(y) & manger(y, x))}
    mange => VbTransSM {\\P Q y x. (P(x) & Q(y) & manger(y, x))}
    mange => VbIntransSM {\\x. manger(x)}
    mange => VbIntransSF {\\x. manger(x)}
    dorment => VbIntransPM {\\P x. (P(x) & dormir(x))}
    dorment => VbIntransPF {\\P x. (P(x) & dormir(x))}
    dort => VbIntransSM {\\P x. (P(x) & dormir(x))}
    dort => VbIntransSF {\\P x. (P(x) & dormir(x))}
    donne => VbTransSM {\\P Q S y x z. (P(x) & Q(y) & S(z) & donner(z, x, y))}
    donne => VbTransSF {\\P Q S y x z. (P(x) & Q(y) & S(z) & donner(z, x, y))}
    souhaite => VbTransSM/VerbeInf {souhaite}
    souhaite => VbTransSF/VerbeInf {souhaite}
    que => (VbIntransSF\\(VbTransSF/VerbeInf))/Phrase {\\P Q x. P(x) & Q(x)}
    que => (VbIntransSM\\(VbTransSM/VerbeInf))/Phrase {\\P Q x. P(x) & Q(x)}
    est => VbIntransSF/AdjFemR {\\P. P}
    est => VbIntransSM/AdjMascL {\\P. P}
    est => VbIntransSF/AdjFemL {\\P. P}
    est => VbIntransSM/AdjMascR {\\P. P}
    est => VbIntransSF/PP {\\P. P}
    est => VbIntransSM/PP {\\P. P}
    donné => PP[Masc] {\\x y z. donner(x, y, z)}
    mangée => PP[Fem] {\\P x y. (P(y) & manger(x, y))}
    donner => VerbeInf {donner}

    # Adverbes
    paisiblement => AdvM {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvF {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvTM {\\P R z. (P(R, z) & paisible(z))}
    paisiblement => AdvTF {\\P R z. (P(R, z) & paisible(z))}

    # Compléments
    à => ((VbIntransSM\\VbTransSM)\\GrNom)/GrNom {\\P Q x. Q(P, x)}
    à => ((VbIntransSF\\VbTransSF)\\GrNom)/GrNom {\\P Q x. Q(P, x)}
    à => (PP[Masc]\\PP[Masc])/GrNom {\\P Q x. Q(P, x)}
    à => (PP[Fem]\\PP[Fem])/GrNom {à}
    à => (VbTransSM\\AnteposMasc)\\VbTransSM {à}
    à => (VbTransSF\\AnteposFem)\\VbTransSF {à}
    A => (PhraseInterro/Phrase)/GrNom[Question] {à}
    avec => (VbIntransSF\\VbIntransSF)/GrNom  {avec}
    avec => (VbIntransSM\\VbIntransSM)/GrNom {\\P Q S x y z. (P(x) & Q(S, z, y) & utilise(z, x))}
    Avec => (PhraseInterro/Phrase)/GrNom[Question] {\\P Q x y. (exists z. (Q(P(x), y) & utilise(x, z)))}
    de => (GrNom[Masc]\\GrNom[Masc])/GrNom {\\P R x y. (P(y) & R(x) & possede(y, x))}
    de => (GrNom[Fem]\\GrNom[Fem])/GrNom {\\P R x y. (P(y) & R(x) & possede(y, x))}
    par => (PP[Masc]\\PP[Masc])/GrNom {\\P Q R x y. (P(x) & Q(R, x, y))}
    par => (PP[Fem]\\PP[Fem])/GrNom {\\P Q R x y. (P(x) & Q(R, x, y))}

    # Conjonctions
    et => (GrNom[MascPlur]/GrNom[Fem])\\GrNom[Masc] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[FemPlur]/GrNom[Fem])\\GrNom[Fem] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Masc] {\\P Q z. (P(z) & Q (z))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Fem] {\\P Q z. (P(z) & Q (z))}
    et => (VbTransSM/VbTransSM)\\VbTransSM {\\P Q z. (P(z) & Q (z))}
    et => (VbTransSF/VbTransSF)\\VbTransSF {\\P Q z. (P(z) & Q (z))}
    et => (VbIntransSF/VbIntransSF)\\VbIntransSF {\\P Q z. (P(z) & Q (z))}
    et => (VbIntransSM/VbIntransSM)\\VbIntransSM {\\P Q z. (P(z) & Q (z))}
    et => (AdjFemL/AdjFemL)\\AdjFemL {\\P Q z. (P(z) & Q (z))}
    et => (AdjFemR/AdjFemR)\\AdjFemR {\\P Q z. (P(z) & Q (z))}
    et => (AdjMascL/AdjMascL)\\AdjMascL {\\P Q z. (P(z) & Q (z))}
    et => (AdjMascR/AdjMascR)\\AdjMascR {\\P Q z. (P(z) & Q (z))}
    et => (Phrase/Phrase)\\Phrase {\\P Q z. (P(z) & Q (z))}

    # Phrases interrogatives
    Quel => (PhraseInterro/VbIntransSM)/Nom[Masc] {\\P R y.(exists x. (R(P, y, x)))}
    quel => GrNom[Question]/Nom[Masc] {quel}
    Quelle => (PhraseInterro/VbIntransSF)/Nom[Fem] {\\P R y.(exists x. (R(P, y, x)))}
    quelle => GrNom[Question]/Nom[Fem] {quel}
    Qui => PhraseInterro/VbIntransSM {\\P x y. P(humain, x, y)}
    Qui => PhraseInterro/VbIntransSF {\\x y z w. (z w) & (y (x w))}
    quoi => GrNom[Question] {\\P. P}
    ? => Phrase\\PhraseInterro {\\P.P}




    #Phrase -> GrNom, Phrase\\GrNom = 1.5
    #Phrase -> Phrase/VbIntransSF, VbIntransSF = 0.5
    #Phrase -> Phrase/VbIntransSM, VbIntransSM = 0.5
    #Phrase -> PhraseInterro, Phrase\\PhraseInterro = 1.0
    #GrNom -> GrNom/Nom, Nom = 2.0
    #GrNom -> GrNom, GrNom\\GrNom = 0.8


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
    La souris est mangée par mon voisin
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
    start_time = time.time()
    ccg = CCGrammar(grammar)
    cpt = 0
    for str in [str1 for str in txt.split("\n") for str1 in [str.strip()] if str1]:
        #print("##########################################################################################")
        #print(f"# Parsing de : \"{str}\" :")
        #print("##########################################################################################\n")
        parses = CCGCKYParser(ccg, str, use_typer = False)
        cpt_n = 0
        if parses:
            for p in parses:
                print(p.show(sem=True))
                print("FIN DU PARSE\n")
                cpt_n += 1
            print(cpt_n, str)
        else:
            print(f"@@@@@@@@@@@@ FAIL on ::: {str} @@@@@@@@@@@@\n")
        cpt += cpt_n
    print("TIME :", time.time() - start_time)
    print("CPT TOTAL", cpt)

txt0 = '''Le chat qui dort est noir
'''

#run(txt)
run(txt)
