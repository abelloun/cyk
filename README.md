<h1 align="center">Combinatory Categorial Grammar Parser using CKY</h1>
<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"></br>
<img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg">
<img src="https://img.shields.io/github/license/abelloun/cyk.svg">
</p>

***
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
![Derivation example of the sentence 'The cat sleeps calmly'.](/image/derivexample.png "Derivation example of the sentence 'The cat sleeps calmly'.")

The CKY algorithm has been adapted for CCG to efficiently parse sentences and provide syntactic and semantic analysis. When constructing the parsing trees, we keep track of the ancestors of each judgement, and reconstruct them at the end using backpointing. This is useful because several different derivations can lead to the same type in one node of the tree, particularly if type raising is used.

It is possible to annotate a word with semantics, which will be taken into account when displayed if the `sem` parameter is set to `True`.\
![Derivation example of the sentence 'The cat sleeps calmly'.](/image/derivexamplesem.png "Derivation example of the sentence 'The cat sleeps calmly'.")

***
### Status, Roadmap, Objectives
<a name="status"></a>
The project is still under development
- [x] Is able to parse a grammar with annotated types
- [x] Is able to manage semantics (with existential and binary operators)
- [x] Is able to compute derivations
- [x] Is able to print the derivations in a concise and human readable way
- [x] Is adaptive (new rules can be easily added) -> But only unary/binary rules for printing !
- [x] Is well documented (pylint scores > 9/10)
- [x] Is well tested (99% coverage)
- [ ] Is not able to compute weights on derivations
- [ ] Does not check cycles in syntax shortcuts of type
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
- **Python 3.10 or above**: The project is developed using Python 3.12. Python 3.10 is needed for pattern matching.

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
![Wrong nltk derivation.](/image/wrongnltk.png "Wrong nltk derivation.")\
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
