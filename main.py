"""
CCG Parser Example

This module demonstrates parsing text using
Combinatory Categorial Grammar (CCG).
It defines a CCG grammar and provides a function to parse a given text input
using the defined grammar rules.
The parsing results are displayed for each sentence, and the module measures
the time taken for parsing and counts the total number of successful parses.

To use this module, you can provide your own CCG grammar rules and sample
text data.
The `run` function parses the text using the specified grammar and displays
the results.

Example usage:
run(TXT_SAMPLE, GRAMMAR)
"""
import time
from CCGCKYParser import CCGCKYParser
from CCGrammar import CCGrammar
from nltk.tree import Tree
from random import randint, choice

GRAMMAR = '''
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
    ma => DetFem  {\\P R x. P(x) & possede(moi, x) & R(x)}
    mon => DetMasc  {\\P R x. P(x) & possede(moi, x) & R(x)}
    mes => DetMascPlur  {\\P R x. P(x) & possede(moi, x) & R(x)}
    mes => DetFemPlur  {\\P R x. P(x) & possede(moi, x) & R(x)}
    ses => DetMascPlur  {\\P R x. exists y. P(x) & possede(y, x) & R(x)}
    ses => DetFemPlur  {\\P R x. exists y. P(x) & possede(y, x) & R(x)}
    un => DetMasc   {\\P R y. exists x. P(x) & R(x)}
    Un => DetMasc   {\\P R y. exists x. P(x) & R(x)}

    # Antépositions
    la => AnteposMasc {\\P. P(\\R x. (féminin(x) & R(x)))}
    le => AnteposMasc {\\P. P(\\R x. (masculin(x) & R(x)))}
    la => AnteposFem {\\P. P(\\R x. (féminin(x) & R(x)))}
    le => AnteposFem {\\P. P(\\R x. (masculin(x) & R(x)))}
    lui => VbTransSM/VbTransSM {\\P S Q R z y x. P(\\T. S(T & (\\u. cible(y))), Q, \\u. R(z), z, y, x)}
    lui => VbTransSF/VbTransSF {\\P S Q R z y x. P(\\T. S(T & (\\u. cible(y))), Q, \\u. R(z), z, y, x)}

    # Adjectifs
    méchant => AdjMascL {\\P. P & méchant}
    méchant => AdjMascR {\\P. P & méchant}
    noir => AdjMascR {\\P. P & noir}
    qui => (GrNom[Fem]\\GrNom[Fem])/VbIntransSF {\\P Q R. P(Q, R)}
    qui => (GrNom[Masc]\\GrNom[Masc])/VbIntransSM {\\P Q R. P(Q, R)}
    qui => (GrNom[FemPlur]\\GrNom[FemPlur])/VbIntransPF {\\P Q R. P(Q, R)}
    qui => (GrNom[MascPlur]\\GrNom[MascPlur])/VbIntransPM {\\P Q R. P(Q, R)}
    donné => PP[Masc] {\\P x. exists y. exists z. donne(x, y, z) & P(y)}
    mangée => PP[Fem] {\\P x. exists y. exists z. mange(x, y) & P(y)}

    # Superlatif
    très => AdjMascL/AdjMascL {\\P. P}
    très => AdjFemL/AdjFemL {\\P. P}
    très => AdjMascR/AdjMascR {\\P. P}
    très => AdjFemR/AdjFemR {\\P. P}

    # Pronoms personnels
    Il => Phrase/VbIntransSM {\\P. P(\\R x. masculin(x) & R(x))}
    Elle => Phrase/VbIntransSF {\\P. P(\\R x. féminin(x) & R(x))}

    # Verbes
    pourchasse => VbTransSF {\\P Q R x. exists y. Q(\\n. P(pourchasse(n) & (\\s. R(n)), y), x)}
    pourchasse => VbTransSM {\\P Q R x. exists y. Q(\\n. P(pourchasse(n) & (\\s. R(n)), y), x)}
    attrape => VbTransSF {\\P Q R x. exists y. Q(\\n. P(attrape(n) & (\\s. R(n)), y), x)}
    attrape => VbTransSM {\\P Q R x. exists y. Q(\\n. P(attrape(n) & (\\s. R(n)), y), x)}
    mange => VbTransSF {\\P Q R x. exists y. Q(\\n. P(mange(n) & (\\s. R(n)), y), x)}
    mange => VbTransSM {\\P Q R x. exists y. Q(\\n. P(mange(n) & (\\s. R(n)), y), x)}
    mange => VbIntransSF {\\P R x. P(R & mange, x)}
    mange => VbIntransSM {\\P R x. P(R & mange, x)}
    dorment => VbIntransPM {\\P R x. P(R & dort, x)}
    dorment => VbIntransPF {\\P R x. P(R & dort, x)}
    dort => VbIntransSM {\\P R x. P(R & dort, x)}
    dort => VbIntransSF {\\P R x. P(R & dort, x)}
    donne => VbTransSM {\\P Q R x. exists y. exists s. P(\\z. Q(\\u. donne(u, z, y) & R(x), x), s)}
    donne => VbTransSF {\\P Q R x. exists y. exists s. P(\\z. Q(\\u. donne(u, z, y) & R(x), x), s)}
    souhaite => VbTransSM/VerbeInf {\\T P Q R x. exists y. exists s. souhaite(T(P, Q, R, x, y, s), x) }
    souhaite => VbTransSF/VerbeInf {\\T P Q R x. exists y. exists s. souhaite(T(P, Q, R, x, y, s), x) }
    que => (VbIntransSF\\(VbTransSF/VerbeInf))/Phrase {\\P Q p. Q(\\S. S(P))}
    que => (VbIntransSM\\(VbTransSM/VerbeInf))/Phrase {\\P Q p. Q(\\U V R x y s. P(R, s, x, y))}
    est => VbIntransSF/AdjFemR {\\P Q R. Q(P(R))}
    est => VbIntransSM/AdjMascL {\\P Q R. Q(P(R))}
    est => VbIntransSF/AdjFemL {\\P Q R. Q(P(R))}
    est => VbIntransSM/AdjMascR {\\P Q R. Q(P(R))}
    est => VbIntransSF/PP[Fem] {\\P Q R x. exists y. Q(\\u. P(R, x, u, y), y)}
    est => VbIntransSM/PP[Masc] {\\P Q R x. exists y. Q(\\u. P(R, x, u, y), y)}
    donner => VerbeInf {\\P Q R x y s. P(\\z. Q(\\u. donne(u, z, y) & R(x), x), s)}

    # Adverbes
    #paisiblement => AdvM {\\P S R. S(R & \\z. paisiblement(P(\\P. P(z), \\x. true)))}
    #paisiblement => AdvF {\\P S R. S(R & \\z. paisiblement(P(\\P. P(z), \\x. true)))}
    paisiblement => AdvM {\\P S R. P(S, paisible & R)}
    paisiblement => AdvF {\\P S R. P(S, paisible & R)}
    paisiblement => AdvTM {\\P S R. P(S, paisible & R)}
    paisiblement => AdvTF {\\P S R. P(S, paisible & R)}

    # Compléments
    à => (VbTransSM\\VbTransSM)\\GrNom {\\P Q S T R x y. Q(P, \\M z. S(\\n. M(x), y), T(R), x, y)}
    à => (VbTransSF\\VbTransSF)\\GrNom  {\\P Q S T R x y. P(Q(T, S, \\z. R(x), y), x)}
    à => (PP[Masc]\\PP[Masc])/GrNom {\\P Q R x y s. Q(\\u. P(\\n. R(y), s), x, y, s)}
    à => (PP[Fem]\\PP[Fem])/GrNom {\\P Q R x y s. Q(\\u. P(\\n. R(y), s), x, y, s)}
    à => (VbTransSM\\AnteposMasc)\\VbTransSM {\\P Q S T R x y s. P(Q(\\O. O), \\M z. S(\\n. M(x), s), T(R), x, s)}
    à => (VbTransSF\\AnteposFem)\\VbTransSF {\\P Q S T R x y. Q(P(T, S, \\z. R(x), y, x))}
    avec => AdvF/GrNom {\\P S Q R x. exists z. S(Q, \\u. P(utilise(z) & \\u. R(z), x, z), z) }
    avec => AdvM/GrNom {\\P S Q R x. exists z. S(Q, \\u. P(utilise(z) & \\u. R(z), x, z), z) }
    de => (GrNom[Masc]/GrNom)\\GrNom[Masc] {\\P Q R u. exists x. Q(\\z. P(R, x) & appartient(x, u), u)}
    de => (GrNom[Fem]/GrNom)\\GrNom[Fem] {\\P Q R u. exists x. Q(\\z. P(R, x) & appartient(x, u), u)}
    par => (PP[Masc]\\PP[Masc])/GrNom {\\P Q R x. exists y. exists s. Q(\\u. P(\\n. R(y), x), x, y, s)}
    par => (PP[Fem]\\PP[Fem])/GrNom {\\P Q R x. exists y. exists s. Q(\\u. P(\\n. R(y), x), x, y, s)}

    # Conjonctions
    et => (GrNom[MascPlur]/GrNom[Fem])\\GrNom[Masc] {\\L C R x. exists y. (L(R, x) & C(R, y))}
    et => (GrNom[FemPlur]/GrNom[Fem])\\GrNom[Fem] {\\L C R x. exists y. (L(R, x) & C(R, y))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Masc] {\\L C R x. exists y. (L(R, x) & C(R, y))}
    et => (GrNom[MascPlur]/GrNom[Masc])\\GrNom[Fem] {\\L C R x. exists y. (L(R, x) & C(R, y))}
    #et => (VbTransSM/VbTransSM)\\VbTransSM {\\P Q T N. P(\\S. S, Q(\\U. U, T))}
    #et => (VbTransSF/VbTransSF)\\VbTransSF {\\P Q T N. P(\\S. S, Q(\\U. U, T))}

    et => (VbTransSM/VbTransSM)\\VbTransSM {\\L C P Q R x. exists y. (L(P, Q, R, x, y) & C(P, Q, R, x, y))}
    #et => (VbTransSM/VbTransSM)\\VbTransSM {\\P Q R x y. Q(\\n. P(pourchasse(n) & (\\s. R(n)), y), x)}             pourchasse(n) & (\\s. R(n))

    # {\\x y. pourchasse(y) & (\\s. R(y))}
    #et => (VbTransSM/VbTransSM)\\VbTransSM {\\L C P Q R x. exists y. L(P, Q(t), C(\\x y. x, \\s n. s(n), R, x, x), x, y)}
    et => (VbTransSF/VbTransSF)\\VbTransSF {\\L C P Q R x. exists y. (L(P, Q, R, x, y) & C(P, Q, R, x, y))}
    et => (VbIntransSF/VbIntransSF)\\VbIntransSF {\\L C P Q x. (L(P, R, x) & C(P, R, x))}
    et => (VbIntransSM/VbIntransSM)\\VbIntransSM {\\L C P Q x. (L(P, R, x) & C(P, R, x))}
    et => (AdjFemL/AdjFemL)\\AdjFemL {\\L C P. (L(P) & C(P))}
    et => (AdjFemR/AdjFemR)\\AdjFemR {\\L C P. (L(P) & C(P))}
    et => (AdjMascL/AdjMascL)\\AdjMascL {\\L C P. (L(P) & C(P))}
    et => (AdjMascR/AdjMascR)\\AdjMascR {\\L C P. (L(P) & C(P))}
    et => (Phrase/Phrase)\\Phrase {\\L C R x. exists y. (C(R, x) & L(R, y))}
    et => (Phrase/Phrase)\\Phrase {\\L C R x. exists y. (C(R, x) & L(R, y))}

    # Phrases interrogatives
    Quel => ((Phrase/Ponct[Interro])/VbIntransSM)/Nom[Masc] {\\P Q R. (Q((\\S. exists x. S(x) & P(x)), R))}
    quel => GrNom[Question]/Nom[Masc] {\\P Q R. (Q((\\S. exists x. S(x) & P(x)), R))}
    Quelle => ((Phrase/Ponct[Interro])/VbIntransSF)/Nom[Fem] {\\P Q R y. (Q((\\S. exists x. S(x) & P(y)), R))}
    quelle => GrNom[Question]/Nom[Fem] {\\P R x. P(x) & R(x)}
    Qui => (Phrase/Ponct[Interro])/VbIntransSM {\\Q R. (Q((\\S. exists x. S(x) & humain(x)), R))}
    Qui => (Phrase/Ponct[Interro])/VbIntransSF {\\Q R. (Q((\\S. exists x. S(x) & humain(x)), R))}
    quoi => GrNom[Question] {\\R x. objet(x) & R(x)}
    Avec => ((Phrase/Ponct[Interro])/Phrase)/GrNom[Question] {\\P S R x z y. P(R, x) & S(\\u. utilise(u, x), y, z) }
    A => ((((Phrase/Ponct[Interro])/PP)/(VbIntransSM/PP[Masc]))/GrNom[Masc])/GrNom[Question] {\\Q S V P I. V(\\R x y s. P(\\u. Q(\\n. R(s), s), x, y, s), S, I)}
    ? => Ponct[Interro] {inconnu}


    Weight("<", GrNom, Phrase\\GrNom) = 1.5
    Weight("<", GrNom, Phrase\\GrNom) = 1.5
    Weight(">", Phrase/VbIntransSF, VbIntransSF) = 0.5
    Weight(">", Phrase/VbIntransSM, VbIntransSM) = 0.5
    Weight("<", PhraseInterro, Phrase\\PhraseInterro) = 1.0
    Weight(">", GrNom/Nom, Nom) = 2.0
    Weight("<", GrNom, GrNom\\GrNom) = 0.8
'''

TXT_SAMPLE = '''
    Un chat dort
    Il dort
    Le chat dort paisiblement
    Le chat noir dort
    Le méchant chat dort
    Le très méchant chat dort
    Le chat de la sœur dort
    Le chat de la sœur de mon voisin dort
    Le chat que mon voisin lui donne mange
    Le chat qui dort est noir
    Le chat mange la souris
    Le chat mange un chat
    Un chat mange un chat
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
    Le rat donne un fromage
    Le rat donne un fromage à la souris
    Un fromage est donné
    Un fromage est donné à la souris
    Un fromage est donné par le rat
    Le chat lui donne la souris
    Un fromage est donné par le rat à la souris
    A quelle souris un fromage est donné par le rat ?
    Le chat le donne à la souris
    Il le lui donne
    mon voisin lui donne le chat
    Il souhaite que mon voisin lui donne le chat
    Il souhaite donner le chat
    Il souhaite donner le chat à mon voisin
    Le chat de mon voisin pourchasse la souris
    Le chat pourchasse et attrape la souris
    Le chat de mon voisin pourchasse et attrape la souris
    La souris dort et le chat de mon voisin attrape la souris
    Le chat dort et la souris dort
    Le chat et la souris dorment
    le chat mange la souris et le fromage
    la souris de mon chat et le fromage dorment
    un fromage très méchant mange le fromage
    le voisin de mon chat mange mon voisin
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
'''

TXT_TEST = '''
Le chat de mon voisin dort
Le chat de la sœur de mon voisin dort
'''

word_test = ""

words = {"chat", "fromage", "rat", "voisin", "sœur", "souris",
         "dents", "la", "le", "mon", "ses", "un", "La", "Le", "Un",
         "méchant", "noir", "donné", "mangée", "très", "Il", "Elle",
          "pourchasse", "attrape", "mange", "dorment", "dort", "donne",
          "souhaite", "est", "donner", "paisiblement", "à", "A",
          "avec", "Avec", "de", "et", "lui", "par", "que", "Quel",
          "quel", "Quelle", "quelle", "qui", "Qui", "quoi", "?"}

mem = set(())

def run_random(grammar):
    ccg = CCGrammar(grammar)
    mem = set()
    with open('output_words.txt', 'a') as f:
        print("Début de l'écriture du fichier")
        while True:
            for i in range(randint((len(mem)//10)+3, len(mem)//10+6), len(mem)//10+8):
                #print(i)
                txt_test = choice(list(words))
                for j in range(i):
                    txt_test += " " + choice(list(words))
                for line in txt_test.splitlines():
                    parses = CCGCKYParser(ccg, line, use_typer=False)
                    if parses:
                        if line not in mem:
                            f.write(line + "\n")
                            print(line)
                            #chart.printCCGDerivation(parse)
                            mem.add(line)
                             #chart.printCCGDerivation(parse)
                        #break


def run(txt, grammar):
    """
    Parse a text input using Combinatory Categorial Grammar (CCG).

    Args:
    - txt (str): A string containing one or more sentences separated by newline
    characters.

    This function parses the input text using Combinatory Categorial Grammar
    (CCG) rules and displays the parsing results for each sentence. It measures
    the time taken for parsing and counts the total number of
    successful parses.

    Example usage:
    run("John loves Mary.\nShe sings a song.")
    """
    start_time = time.time()

    # Create a CCGrammar object from the grammar.
    ccg = CCGrammar(grammar)
    cpt = 0
    #
    #print(ccg.show())
    # Split the input 'txt' by newline characters to
    # process each sentence separately.
    for sentence in (str1.strip() for str1 in txt.split("\n") if str1.strip()):
        # Print the sentence being parsed.
        # print("##########################################################")
        # print(f"# Parsing of: \"{sentence}\":")
        # print("##########################################################\n")
        # Use the CCGCKYParser to parse the current sentence,
        # setting 'use_typer' to False.
        parses = CCGCKYParser(ccg, sentence, use_typer=False)
        cpt_n = 0

        if parses and word_test in sentence:
            # Iterate through the parsing results and display them.
            for parse in parses:
                #print(parse.show(sem=True))
                #print(parse.to_nltk_tree())
                print(parse.current.expr.show(), '\n', parse.current.sem.show(), '\n')
                # cpt_n += 1
                #break
            #print(sentence, " : ", cpt_n, "parses valides")
        else:
            # Handle cases where parsing fails.
            #print(f"@@@@@@@@@@@@ FAIL on ::: {sentence} @@@@@@@@@@@@\n")
            pass
        cpt += cpt_n

    # Calculate and display the time taken for parsing.
    print("TIME:", time.time() - start_time)

    # Display the total count of successful parses.
    print("CPT TOTAL", cpt)


# run(TXT_SAMPLE, GRAMMAR)
run_random(GRAMMAR)
