# Combinatory Categorial Grammar Parser using CKY
***
    - Une description générale du système ou du projet.
    - Le statut du projet, qui est surtout utile lorsqu’il est encore en stade du développement. Évoquez les modifications prévues et l’objectif du développement ou signalez clairement que le développement du projet est terminé.
    - Les exigences concernant l’environnement de développement en vue de son intégration.
    - Une instruction pour l’installation et l’utilisation.
    - Une liste des technologies utilisées et, le cas échéant, des liens vers d’autres informations sur ces technologies.
    - Les projets open source que les développeurs modifient ou complètent par eux-mêmes doivent être complétés par un paragraphe « collaboration souhaitée » dans leur fichier readme.md. Comment contourner un problème ? Comment les développeurs doivent-ils appliquer les modifications ?
    - Bugs connus et corrections éventuelles apportées.
    - Section FAQ reprenant toutes les questions posées jusqu’à présent.
    - Droits d’auteurs et informations sur la licence.


## Table of Contents
1. [General Informations](#general-info)
2. [Status, Roadmap, Objectives](#status)
3. [Requirements and Installation](#installation)
4. [Collaboration](#collaboration)
5. [Known issues](#bugs)
5. [FAQs](#faqs)
6. [License](#license)
7. [Miscellaneous](#extra)

***
### General Informations
<a name="general-info"></a>
This repository contains the implementation of the [CKY (Cocke-Kasami-Younger) algorithm](https://en.wikipedia.org/wiki/CYK_algorithm) for parsing natural language sentences using [Combinatory Categorial Grammar (CCG)](https://en.wikipedia.org/wiki/Combinatory_categorial_grammar). 

CCG is a linguistically motivated grammar formalism that offers flexibility in representing both syntax and semantics.

There are two kind of types :
- Primitives types (*Sentence, Noun, Adverb, ...)*
- Complex types, schematizable as X/Y and X\Y *(Sentence/Noun, Adverb\\Verb, ...)*\
    An element of type X/Y (resp. X/Y) expects an element of type Y to its right (resp. left), and returns an element of type X

Syntax shortcuts can be defined in the grammar using the `::` operator.\
*Example :*
```
AdjMascL :: N[Masc]/N[Masc]
mad => AdjMascL

...is the same as...
mad => N[Masc]/N[Masc]
```



Our implementation allows application and combination rules, and it is also possible to activate the type raising by setting `use_typer` as `True` in the parser. *(The type raising only operates on primitive types)*

*Example :*\
![Derivation example of the sentence 'The cat sleeps calmly'.](/image/derivexample "Derivation example of the sentence 'The cat sleeps calmly'.")

The CKY algorithm has been adapted for CCG to efficiently parse sentences and provide syntactic and semantic analysis. When constructing the parsing trees, we keep track of the ancestors of each judgement, and reconstruct them at the end using backpointing. This is useful because several different derivations can lead to the same type in one node of the tree, particularly if type raising is used.

It is possible to annotate a word with semantics, which will be taken into account when displayed if the `sem` parameter is set to `True`.\
![Derivation example of the sentence 'The cat sleeps calmly'.](/image/derivexamplesem "Derivation example of the sentence 'The cat sleeps calmly'.")

***
### Status, Roadmap, Objectives
<a name="status"></a>
The project is still under development
- [x] Is able to parse a grammar with annotated types
- [x] Is able to manage semantics (with existential and binary operators)
- [x] Is able to compute derivations
- [x] Is able to print the derivations in a concise and human readable way
- [x] Is adaptive (new rules can be easily added) -> But only unary/binary rules for printing !
- [ ] Is not able to compute weights on derivations
- [ ] Is not well documented
- [ ] Does not check cycles in syntax shortcuts of type
- [ ] Has not yet been formally tested
- [ ] Does not come with a sentence generator using the parsed grammar
- [ ] Does not handle errors cleanly (unclear error messages)

We also give a grammar sample, which is unfinished
- [x] All correct sentences can be parsed
- [x] Not too ambiguous 
- [ ] Semantics are still a bit cobbled together, but mainly work
- [ ] Can manage subjunctive sentences
- [ ] Does not yet have consistent weights on derivations

***
### Requirements and Installation
<a name="installation"></a>
- **Python 3.12 or above**: The project is developed using Python 3.12.

- **RDParser**: The `RDParser` library is incorporated to enhance parsing capabilities. This external dependency enables the project to work with CCG grammar rules and lexicon entries efficiently.

Make sure to have these libraries installed and compatible with your Python environment for the project to function correctly.
***
### Collaboration
<a name="collaboration"></a>
Contributions are welcome, but we don't yet have a guideline for this, so please don't hesitate to contact us.
***
### Known issues
<a name="bugs"></a>
- It is not possible to display derivations using ternary rules or more.
- Error messages are not precise at all.

***
### FAQs
<a name="faqs"></a>
- Why not use nltk ?

We have decided not to use the nltk library, which contains bugs. Here is an example of a derivation which should not be allowed.\
![Wrong nltk derivation.](/image/wrongnltk "Wrong nltk derivation.")\
Some derivations are also forgotten.
***
### License
<a name="license"></a>
This project is released under the [MIT License](LICENSE) as specified in the [LICENSE](LICENSE) file.
***
### Miscellaneous
<a name="extra"></a>
#### References

- CCGbank: A Corpus of CCG Derivations and Dependency Structures Extracted from the Penn Treebank. J. Hockenmaier, M. Steedman. https://doi.org/10.1162/coli.2007.33.3.355

