from CCGrammar import CCGrammar
from CCGCKYParser import CCGCKYParser, CKYDerivation
import time

grammar = '''
    :- Phrase, GrNom, Nom
    :- VerbeInf, Ponct, PP

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
    chat => Nom[Masc] {chat}                                       
    fromage => Nom[Masc] {fromage}
    rat => Nom[Masc] {rat}
    voisin => Nom[Masc] {voisin}
    sœur => Nom[Fem] {soeur}
    souris => Nom[Fem] {souris}
    souris => Nom[FemPlur] {souris}
    dents => Nom[FemPlur] {dents}

    # Déterminants
    la => DetFem {\\P R x. P(x) & R(x)}
    le => DetMasc  {\\P R x. P(x) & R(x)}
    La => DetFem  {\\P R x. P(x) & R(x)}
    Le => DetMasc   {\\P R x. P(x) & R(x)}
    ma => DetFem  {\\P R x. P(x) & R(x)}
    mon => DetMasc  {\\P R x. P(x) & R(x)}
    mes => DetMascPlur  {\\P R x. P(x) & R(x)}
    mes => DetFemPlur  {\\P R x. P(x) & R(x)}
    ses => DetMascPlur  {\\P R x. P(x) & R(x)}
    ses => DetFemPlur  {\\P R x. P(x) & R(x)}
    un => DetMasc   {\\P R. exists x. P(x) & R(x)}
    Un => DetMasc   {\\P R. exists x. P(x) & R(x)}

    # Antépositions
    la => AnteposMasc {\\P. P(\\R x. (féminin(x) & R(x)))}
    le => AnteposMasc {\\P. P(\\R x. (masculin(x) & R(x)))}
    la => AnteposFem {\\P. P(\\R x. (féminin(x) & R(x)))}
    le => AnteposFem {\\P. P(\\R x. (masculin(x) & R(x)))}
    lui => VbTransSM/VbTransSM {\\P S Q R x z. P(\\T. S(T & (\\u. masculin(x))), Q, R, z)}
    lui => VbTransSF/VbTransSF {\\P S Q R x z. P(\\T. S(T & (\\u. masculin(x))), Q, R, z)}

    # Adjectifs
    méchant => AdjMascL {\\P. P & méchant}
    méchant => AdjMascR {\\P. P & méchant}
    noir => AdjMascR {\\P. P & noir}
    qui => (GrNom[Fem]\\GrNom[Fem])/VbIntransSF {\\P Q R. P(Q, R)}
    qui => (GrNom[Masc]\\GrNom[Masc])/VbIntransSM {\\P Q R. P(Q, R)}
    qui => (GrNom[FemPlur]\\GrNom[FemPlur])/VbIntransPF {\\P Q R. P(Q, R)}
    qui => (GrNom[MascPlur]\\GrNom[MascPlur])/VbIntransPM {\\P Q R. P(Q, R)}
    donné => PP[Masc] {\\P x y z. donne(x, y, z) & P(y, z)}
    mangée => PP[Fem] {\\P x y z. mange(x, y, z) & P(y)}

    # Superlatif
    très => AdjMascL/AdjMascL {\\P. P}
    très => AdjFemL/AdjFemL {\\P. P}
    très => AdjMascR/AdjMascR {\\P. P}
    très => AdjFemR/AdjFemR {\\P. P}

    # Pronoms personnels
    Il => Phrase/VbIntransSM {\\P. P(\\R x. masculin(x) & R(x))}
    Elle => Phrase/VbIntransSF {\\P. P(\\R x. féminin(x) & R(x))}
    # Verbes
    pourchasse => VbTransSF {\\P Q R x. P(pourchasse(x)) & Q(R, x)}
    pourchasse => VbTransSM {\\P Q R x. P(pourchasse(x)) & Q(R, x)}
    attrape => VbTransSF {\\P Q R x. P(attrape(x)) & Q(R, x)}
    attrape => VbTransSM {\\P Q R x. P(attrape(x)) & Q(R, x)}
    mange => VbTransSF {\\P Q R x. P(mange(x)) & Q(R, x)}
    mange => VbTransSM {\\P Q R x. P(mange(x)) & Q(R, x)}

    mange => VbIntransSF {\\P R. P(R & mange)}
    mange => VbIntransSM {\\P R. P(R & mange)}
    dorment => VbIntransPM {\\P R. P(R & dort)}
    dorment => VbIntransPF {\\P R. P(R & dort)}
    dort => VbIntransSM {\\P R. P(R & dort)}
    dort => VbIntransSF {\\P R. P(R & dort)}
    donne => VbTransSM {\\P Q R x. P(donne(x)) & Q(R, x)}
    donne => VbTransSF {\\P Q R x. P(donne(x)) & Q(R, x)}
    souhaite => VbTransSM/VerbeInf {souhaite}
    souhaite => VbTransSF/VerbeInf {souhaite}
    que => (VbIntransSF\\(VbTransSF/VerbeInf))/Phrase {\\P Q x. P(x) & Q(x)}
    que => (VbIntransSM\\(VbTransSM/VerbeInf))/Phrase {\\P Q x. P(x) & Q(x)}
    est => VbIntransSF/AdjFemR {\\P Q R. Q(P(R))}
    est => VbIntransSM/AdjMascL {\\P Q R. Q(P(R))}
    est => VbIntransSF/AdjFemL {\\P Q R. Q(P(R))}
    est => VbIntransSM/AdjMascR {\\P Q R. Q(P(R))}
    est => VbIntransSF/PP {\\P Q R. P(Q(R))}
    est => VbIntransSM/PP {\\P Q R. P(Q(R))}
    donner => VerbeInf {donner}

    # Adverbes
    paisiblement => AdvM {\\P S R. P(S, paisible & R)}
    paisiblement => AdvF {\\P S R. P(S, paisible & R)}
    paisiblement => AdvTM {\\P S R. P(S, paisible & R)}
    paisiblement => AdvTF {\\P S R. P(S, paisible & R)}

    # Compléments
    à => (VbTransSM\\VbTransSM)\\GrNom {\\P Q S T R. S(\\z. P(Q(\\U. T(U(z) & R), transfert, z)))}
    à => (VbTransSF\\VbTransSF)\\GrNom  {\\P Q S T R. S(\\z. P(Q(\\U. T(U(z) & R), transfert, z)))}

    à => (PP[Masc]\\PP[Masc])/GrNom {\\P Q R z. P(Q(\\s. R, z))}
    à => (PP[Fem]\\PP[Fem])/GrNom {\\P Q R z. P(Q(\\s. R, z))}
    à => (VbTransSM\\AnteposMasc)\\VbTransSM {\\P Q S T R. S(\\z. Q(\\M.M, P(\\U. T(U(z) & R), transfert, z)))}
    à => (VbTransSF\\AnteposFem)\\VbTransSF {\\P Q S T R. S(\\z. Q(\\M.M, P(\\U. T(U(z) & R), transfert, z)))}

    avec => AdvF/GrNom {\\P S Q R x z. P(utilise(z), x) & S(Q, R, z) }
    avec => AdvM/GrNom {\\P S Q R x z. P(utilise(z), x) & S(Q, R, z) }
    de => (GrNom[Masc]\\GrNom[Masc])/GrNom {\\P Q S y x. P(appartient(y) & (\\z. Q(S, y)), x)}
    de => (GrNom[Fem]\\GrNom[Fem])/GrNom {\\P Q S y x. P(appartient(y) & (\\z. Q(S, y)), x)}
    par => (PP[Masc]\\PP[Masc])/GrNom {\\Q R P x y. Q((\\u. R(P,u,y)), x)}
    par => (PP[Fem]\\PP[Fem])/GrNom {\\Q R P x y. Q((\\u. R(P,u,y)), x)}

    # Conjonctions
    et => (GrNom[MascPlur]/GrNom[Fem])\\GrNom[Masc] {\\P Q R. (P(R) & Q(R))}
    et => (GrNom[FemPlur]/GrNom[Fem])\\GrNom[Fem] {\\P Q R. (P(R) & Q(R))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Masc] {\\P Q R. (P(R) & Q(R))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Fem] {\\P Q R. (P(R) & Q(R))}
    #et => (VbTransSM/VbTransSM)\\VbTransSM {\\P Q T N. P(\\S. S, Q(\\U. U, T))}
    #et => (VbTransSF/VbTransSF)\\VbTransSF {\\P Q T N. P(\\S. S, Q(\\U. U, T))}

    et => (VbTransSM/VbTransSM)\\VbTransSM {\\P Q R. (P(R) & Q(R))}
    et => (VbTransSF/VbTransSF)\\VbTransSF {\\P Q R. (P(R) & Q(R))}
    et => (VbIntransSF/VbIntransSF)\\VbIntransSF {\\P Q R. (P(R) & Q(R))}
    et => (VbIntransSM/VbIntransSM)\\VbIntransSM {\\P Q R. (P(R) & Q(R))}
    et => (AdjFemL/AdjFemL)\\AdjFemL {\\P Q R. (P(R) & Q(R))}
    et => (AdjFemR/AdjFemR)\\AdjFemR {\\P Q R. (P(R) & Q(R))}
    et => (AdjMascL/AdjMascL)\\AdjMascL {\\P Q R. (P(R) & Q(R))}
    et => (AdjMascR/AdjMascR)\\AdjMascR {\\P Q R. (P(R) & Q(R))}
    et => (Phrase/Phrase)\\Phrase {\\P Q R. (P(R) & Q(R))}

    # Phrases interrogatives
    Quel => ((Phrase/Ponct[Interro])/VbIntransSM)/Nom[Masc] {\\P Q R. (exists x. Q((\\z. P), R, x) & R(x))}
    quel => GrNom[Question]/Nom[Masc] {\\P R x. P(x) & R(x) & inconnu(x)}
    Quelle => ((Phrase/Ponct[Interro])/VbIntransSF)/Nom[Fem] {\\P Q R. (exists x. Q((\\z. P), R, x) & R(x))}
    quelle => GrNom[Question]/Nom[Fem] {\\P R x. P(x) & R(x) & inconnu(x)}
    Qui => (Phrase/Ponct[Interro])/VbIntransSM {\\Q R. (exists x. Q((\\z. (\\x. humain(x))), R, x) & R(x))}
    Qui => (Phrase/Ponct[Interro])/VbIntransSF {\\Q R. (exists x. Q((\\z. (\\x. humain(x))), R, x) & R(x))}
    quoi => GrNom[Question] {\\R x. objet(x) & R(x)}
    Avec => ((Phrase/Ponct[Interro])/Phrase)/GrNom[Question] {\\P S R x z. P(R, x) & S(\\s. utilise(s, x), z) }
    A => ((Phrase/Ponct[Interro])/Phrase)/GrNom[Question] {\\P. P}
    ? => Ponct[Interro] {inconnu}


    Weight("<", GrNom, Phrase\\GrNom) = 1.5
    Weight("<", GrNom, Phrase\\GrNom) = 1.5
    Weight(">", Phrase/VbIntransSF, VbIntransSF) = 0.5
    Weight(">", Phrase/VbIntransSM, VbIntransSM) = 0.5
    Weight("<", PhraseInterro, Phrase\\PhraseInterro) = 1.0
    Weight(">", GrNom/Nom, Nom) = 2.0
    Weight("<", GrNom, GrNom\\GrNom) = 0.8


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
