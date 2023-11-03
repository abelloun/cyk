"""
CCG Types Module

This module defines classes and utilities for working with Combinatory Categorial
Grammar (CCG) types, a formalism used in natural language processing for
semantic composition.
It includes classes for CCG types, type unification, type variables, atomic types,
composite types, annotations, and type operations.

Classes:
- CCGType: Represents CCG types and provides methods for type unification.
- CCGTypeVar: Represents a CCG type variable.
- CCGTypeAtomicVar: Represents an atomic CCG type with a variable.
- CCGTypeAtomic: Represents an atomic CCG type.
- CCGTypeComposite: Represents a composite CCG type.
- CCGTypeAnnotation: Represents a CCG type with an annotation.

The module aims to assist in working with CCG types and type operations in natural
language understanding and parsing tasks.
"""

################################################
## CCG Types
################################################
class CCGType:
    """
    Represents a Combinatory Categorial Grammar (CCG) type for semantic composition.

    This class provides a representation of CCG types and methods for type unification.

    Class Attributes:
    - count (int): A class-level counter used for generating fresh variable names.

    Methods:
    - `fresh(var)`: Generate a fresh variable name based on the input variable.
    - `reset()`: Reset the class-level counter for generating fresh variable names.
    - `unify(left, right, sigma)`: Attempt to unify two CCG types and update a type substitution.

    Args:
    - left (CCGType): The left type for unification.
    - right (CCGType): The right type for unification.
    - sigma (dict): A type substitution to update.

    Returns:
    bool: True if unification is successful; False otherwise.

    Example:
    >>> t1 = CCGTypeAtomicVar("X")
    >>> t2 = CCGTypeAtomicVar("Y")
    >>> sigma = {}
    >>> result = CCGType.unify(t1, t2, sigma)

    >>> print(CCGType.fresh("X"))
    "X_0"
    """
    count = -1

    @classmethod
    def fresh(cls, var):
        """
        Generate a fresh variable name based on the input variable.

        Args:
        - var (str): The base variable name.

        Returns:
        str: A fresh variable name.

        Example:
        >>> base_var = "X"
        >>> fresh_var = CCGType.fresh(base_var)
        >>> print(fresh_var)
        "X_0"
        """
        cls.count += 1
        return f"{var.split('_')[0]}_{cls.count}"

    @classmethod
    def reset(cls):
        """
        Reset the class-level counter for generating fresh variable names.

        Example:
        >>> CCGType.reset()
        """
        cls.count = -1

    @classmethod
    def unify(cls, left, right, sigma):
        """
        Attempt to unify two CCG types and update a type substitution.

        Args:
        - left (CCGType): The left type for unification.
        - right (CCGType): The right type for unification.
        - sigma (dict): A type substitution to update.

        Returns:
        bool: True if unification is successful; False otherwise.

        Example:
        >>> t1 = CCGTypeAtomicVar("X")
        >>> t2 = CCGTypeAtomicVar("Y")
        >>> sigma = {}
        >>> result = CCGType.unify(t1, t2, sigma)
        >>> print(result)
        True
        >>> print(sigma)
        {"X": CCGTypeAtomicVar("Y")}
        """
        def up_res(substitution):
            nonlocal result
            result = True
            sigma.update(substitution)

        result = False

        match(left, right):

            case (CCGTypeVar(name=name1), CCGTypeVar(name=name2)):
                if name1 != name2:
                    up_res({name1: CCGTypeVar(name2)})

            case (CCGTypeVar(name=name), any_type):
                up_res({name: any_type})

            case (any_type, CCGTypeVar(name=name)):
                up_res({name: any_type})

            case (CCGTypeAtomicVar(name=name1), CCGTypeAtomicVar(name=name2)):
                if name1 != name2:
                    up_res({name1: CCGTypeAtomicVar(name2)})

            case (CCGTypeAtomicVar(name=name1), CCGTypeAtomic(name=name2)):
                up_res({name1: CCGTypeAtomic(name2)})

            case (CCGTypeAtomic(name=name2), CCGTypeAtomicVar(name=name1)):
                up_res({name1: CCGTypeAtomic(name2)})

            case (CCGTypeAtomicVar(name=name1), CCGTypeAnnotation(ccgtype=CCGTypeAtomic(name=name2), annot=annot)):
                up_res({name1: CCGTypeAnnotation(ccgtype=CCGTypeAtomic(name2), annot=annot)})

            case (CCGTypeAnnotation(type=CCGTypeAtomic(name=name2), annot=annot), CCGTypeAtomicVar(name=name1)):
                up_res({name1: CCGTypeAnnotation(ccgtype=CCGTypeAtomic(name2), annot=annot)})

            case (CCGTypeAtomic(name=name1), CCGTypeAtomic(name=name2)):
                result = name1 == name2

            case (CCGTypeAnnotation(type=t1, annot=annot1), CCGTypeAnnotation(type=t2, annot=annot2)):
                result = annot1 == annot2 and cls.unify(t1, t2, sigma)

            case (CCGTypeAnnotation(type=t1, annot=annot1), any_type):
                result = cls.unify(t1, any_type, sigma)

            case (any_type, CCGTypeAnnotation(type=t2, annot=annot2)):
                result = cls.unify(any_type, t2, sigma)

            case (CCGTypeComposite(dir=dir1, left=left1, right=right1), CCGTypeComposite(dir=dir2, left=left2, right=right2)):
                same_dir = dir1 == dir2
                unif_left = cls.unify(left1, left2, sigma)
                unif_right = cls.unify(right1.replace(sigma), right2.replace(sigma), sigma)
                result = same_dir and unif_left and unif_right

        return result

class CCGTypeVar(CCGType):
    """
    Represents a CCG type variable.

    This class represents a variable in Combinatory Categorial Grammar (CCG) types.

    Args:
    - name (str): The name of the CCG type variable.

    Example:
    >>> type_variable = CCGTypeVar("X")
    """

    def __init__(self, name):
        """
        Initialize a CCGTypeVar object with a type variable.

        Args:
        - name (str): The name of the CCG type variable.

        Example:
        >>> type_variable = CCGTypeVar("X")
        """
        self.name = name

    def show(self):
        """
        Return a string representation of the CCGTypeVar.

        Returns:
        str: A string representation of the CCGTypeVar with the type variable.

        Example:
        >>> type_variable = CCGTypeVar("X")
        >>> print(type_variable.show())
        """
        return f"${self.name}"

    def expand(self, name, ccgtype):
        """
        Expand type variables in the CCGTypeVar.

        Args:
        - name (str): The name of the type variable to expand.
        - ccgtype (CCGType): The replacement CCG type.

        Returns:
        CCGType: The same CCGType if the type variable names match, or the replacement
                 CCG type if they don't.

        Example:
        >>> type_variable = CCGTypeVar("X")
        >>> new_name = "Y"
        >>> new_type = CCGTypeAtomic("NP")
        >>> expanded_type = type_variable.expand(new_name, new_type)
        """
        return ccgtype if self.name == name else self

    def replace(self, sigma):
        """
        Replace type variables in the CCGTypeVar using a substitution dictionary.

        Args:
        - sigma (dict): A dictionary that maps type variable names to CCGType
                        objects for substitution.

        Returns:
        CCGType: The CCGType object resulting from the replacement if the type variable
        name is in the substitution dictionary, or the original CCGTypeVar if not.

        Example:
        >>> type_variable = CCGTypeVar("X")
        >>> substitution = {"X": CCGTypeAtomic("NP")}
        >>> replaced_type = type_variable.replace(substitution)
        """
        if self.name not in sigma:
            return self
        if isinstance(sigma[self.name], CCGTypeVar):
            return sigma[self.name].replace(sigma)
        return sigma[self.name]


class CCGTypeAtomicVar(CCGType):
    """
    Represents an atomic CCG type with a variable.

    This class represents an atomic Combinatory Categorial Grammar (CCG) type
    that includes a type variable.

    Args:
    - name (str): The name of the type variable.

    Example:
    >>> atomic_var_type = CCGTypeAtomicVar("X")
    """

    def __init__(self, name):
        """
        Initialize a CCGTypeAtomicVar object with a type variable.

        Args:
        - name (str): The name of the type variable.

        Example:
        >>> atomic_var_type = CCGTypeAtomicVar("X")
        """
        self.name = name

    def show(self):
        """
        Return a string representation of the CCGTypeAtomicVar.

        Returns:
        str: A string representation of the CCGTypeAtomicVar with the type variable.

        Example:
        >>> atomic_var_type = CCGTypeAtomicVar("X")
        >>> print(atomic_var_type.show())
        """
        return f"@{self.name}"

    def expand(self, name, ccgtype):
        """
        Expand type variables in the CCGTypeAtomicVar.

        Args:
        - name (str): The name of the type variable to expand.
        - ccgtype (CCGType): The replacement CCG type.

        Returns:
        CCGType: The same CCGType if the type variable names match, or the
                 replacement CCG type if they don't.

        Example:
        >>> atomic_var_type = CCGTypeAtomicVar("X")
        >>> new_name = "Y"
        >>> new_type = CCGTypeAtomic("NP")
        >>> expanded_type = atomic_var_type.expand(new_name, new_type)
        """
        return ccgtype if self.name == name else self

    def replace(self, sigma):
        """
        Replace type variables in the CCGTypeAtomicVar using a substitution
        dictionary.

        Args:
        - sigma (dict): A dictionary that maps type variable names to CCGType
                        objects for substitution.

        Returns:
        CCGType: The CCGType object resulting from the replacement if the type
        variable name is in the substitution dictionary,
        or the original CCGTypeAtomicVar if not.

        Example:
        >>> atomic_var_type = CCGTypeAtomicVar("X")
        >>> substitution = {"X": CCGTypeAtomic("NP")}
        >>> replaced_type = atomic_var_type.replace(substitution)
        """
        return sigma[self.name] if self.name in sigma else self


class CCGTypeAtomic(CCGType):
    """
    Represents an atomic CCG type.

    This class represents an atomic Combinatory Categorial Grammar (CCG) type,
    which is a basic, indivisible type.

    Args:
    - name (str): The name of the atomic type.

    Example:
    >>> atomic_type = CCGTypeAtomic("N")
    """

    def __init__(self, name):
        """
        Initialize a CCGTypeAtomic object.

        Args:
        - name (str): The name of the atomic type.

        Example:
        >>> atomic_type = CCGTypeAtomic("N")
        """
        self.name = name

    def show(self):
        """
        Return a string representation of the CCGTypeAtomic.

        Returns:
        str: A string representation of the CCGTypeAtomic.

        Example:
        >>> atomic_type = CCGTypeAtomic("N")
        >>> print(atomic_type.show())
        """
        return self.name

    def expand(self, name, ccgtype):
        """
        Expand type variables in the CCGTypeAtomic.

        Args:
        - name (str): The name of the type variable to expand.
        - ccgtype (CCGType): The replacement CCG type.

        Returns:
        CCGType: The same CCGType if the names match or the replacement type
                if they don't.

        Example:
        >>> atomic_type = CCGTypeAtomic("X")
        >>> new_name = "Y"
        >>> new_type = CCGTypeAtomic("NP")
        >>> expanded_type = atomic_type.expand(new_name, new_type)
        """
        return ccgtype if self.name == name else self

    def replace(self, _):
        """
        Replace type variables in the CCGTypeAtomic.

        This method does not perform any_type replacements because atomic types
        do not contain type variables.

        Args:
        - _: A placeholder argument (not used).

        Returns:
        CCGTypeAtomic: The same CCGTypeAtomic object without modifications.

        Example:
        >>> atomic_type = CCGTypeAtomic("N")
        >>> substitution = {"X": CCGTypeAtomic("NP")}
        >>> replaced_type = atomic_type.replace(substitution)
        """
        return self


class CCGTypeComposite(CCGType):
    """
    Represents a composite CCG type.

    This class represents a composite Combinatory Categorial Grammar (CCG) type.
    A composite type is constructed from two
    component types and a direction (forward or backward).

    Args:
    - dir (bool): The direction of the composite type. True for forward (e.g., NP/N),
     False for backward (e.g., N\\NP).
    - left (CCGType): The left component type of the composite.
    - right (CCGType): The right component type of the composite.

    Example:
    >>> dir = True  # Forward direction
    >>> left_type = CCGTypeAtomic("NP")
    >>> right_type = CCGTypeAtomic("N")
    >>> ccg_type = CCGTypeComposite(dir, left_type, right_type)
    """

    def __init__(self, direction, left, right):
        """
        Initialize a CCGTypeComposite object.

        Args:
        - direction (bool): The direction of the composite type. True for forward,
        False for backward.
        - left (CCGType): The left component type of the composite.
        - right (CCGType): The right component type of the composite.

        Example:
        >>> dir = True  # Forward direction
        >>> left_type = CCGTypeAtomic("NP")
        >>> right_type = CCGTypeAtomic("N")
        >>> ccg_type = CCGTypeComposite(dir, left_type, right_type)
        """
        self.dir = direction
        self.left = left
        self.right = right

    def show(self):
        """
        Return a string representation of the CCGTypeComposite.

        Returns:
        str: A string representation of the CCGTypeComposite.

        Example:
        >>> ccg_type = CCGTypeComposite(True, CCGTypeAtomic("NP"), CCGTypeAtomic("N"))
        >>> print(ccg_type.show())
        """
        slash = "/" if self.dir else "\\"
        return f"({self.left.show()} {slash} {self.right.show()})"

    def expand(self, name, ccgtype):
        """
        Expand type variables in the CCGTypeComposite.

        Args:
        - name (str): The name of the type variable to expand.
        - ccgtype (CCGType): The replacement CCG type.

        Returns:
        CCGTypeComposite: A new CCGTypeComposite with type variables expanded.

        Example:
        >>> dir = False  # Backward direction
        >>> left_type = CCGTypeVariable("X")
        >>> right_type = CCGTypeAtomic("N")
        >>> ccg_type = CCGTypeComposite(dir, left_type, right_type)
        >>> new_name = "Y"
        >>> new_type = CCGTypeAtomic("NP")
        >>> expanded_type = ccg_type.expand(new_name, new_type)
        """
        lexp = self.left.expand(name, ccgtype)
        rexp = self.right.expand(name, ccgtype)
        return CCGTypeComposite(self.dir, lexp, rexp)

    def replace(self, sigma):
        """
        Replace type variables in the CCGTypeComposite using a substitution dictionary.

        Args:
        - sigma (dict): A dictionary that maps type variable names to replacement
                        CCG types.

        Returns:
        CCGTypeComposite: A new CCGTypeComposite with type variables replaced
                            according to the substitution.

        Example:
        >>> dir = True  # Forward direction
        >>> left_type = CCGTypeVariable("X")
        >>> right_type = CCGTypeAtomic("N")
        >>> ccg_type = CCGTypeComposite(dir, left_type, right_type)
        >>> substitution = {"X": CCGTypeAtomic("NP")}
        >>> replaced_type = ccg_type.replace(substitution)
        """
        lrep = self.left.replace(sigma)
        rrep = self.right.replace(sigma)
        return CCGTypeComposite(self.dir, lrep, rrep)


class CCGTypeAnnotation(CCGType):
    """
    Represents a CCG type with an annotation.

    This class represents a Combinatory Categorial Grammar (CCG) type with an
    annotation. It extends the base CCGType class and includes an additional
    annotation for the type.

    Args:
    - type (CCGType): The base CCG type without an annotation.
    - annot (str): The annotation for the type.

    Example:
    >>> base_type = CCGTypeAtomic("NP")
    >>> annotation = "SBJ"
    >>> ccg_type = CCGTypeAnnotation(base_type, annotation)
    """

    def __init__(self, ccgtype, annot):
        """
        Initialize a CCGTypeAnnotation object.

        Args:
        - type (CCGType): The base CCG type without an annotation.
        - annot (str): The annotation for the type.

        Example:
        >>> base_type = CCGTypeAtomic("NP")
        >>> annotation = "SBJ"
        >>> ccg_type = CCGTypeAnnotation(base_type, annotation)
        """
        self.type = ccgtype
        self.annot = annot

    def show(self):
        """
        Return a string representation of the CCGTypeAnnotation.

        Returns:
        str: A string representation of the CCGTypeAnnotation.

        Example:
        >>> ccg_type = CCGTypeAnnotation(CCGTypeAtomic("NP"), "SBJ")
        >>> print(ccg_type.show())
        """
        return f"{self.type.show()}[{self.annot}]"

    def expand(self, name, ccgtype):
        """
        Expand type variables in the CCGTypeAnnotation.

        Args:
        - name (str): The name of the type variable to expand.
        - type (CCGType): The replacement CCG type.

        Returns:
        CCGTypeAnnotation: A new CCGTypeAnnotation with type variables expanded.

        Example:
        >>> base_type = CCGTypeVariable("X")
        >>> annotation = "OBJ"
        >>> ccg_type = CCGTypeAnnotation(base_type, annotation)
        >>> new_name = "Y"
        >>> new_type = CCGTypeAtomic("NP")
        >>> expanded_type = ccg_type.expand(new_name, new_type)
        """
        return CCGTypeAnnotation(self.type.expand(name, ccgtype), self.annot)

    def replace(self, sigma):
        """
        Replace type variables in the CCGTypeAnnotation using a substitution
        dictionary.

        Args:
        - sigma (dict): A dictionary that maps type variable names to replacement
                        CCG types.

        Returns:
        CCGTypeAnnotation: A new CCGTypeAnnotation with type variables replaced
                            according to the substitution.

        Example:
        >>> base_type = CCGTypeVariable("X")
        >>> annotation = "SBJ"
        >>> ccg_type = CCGTypeAnnotation(base_type, annotation)
        >>> substitution = {"X": CCGTypeAtomic("NP")}
        >>> replaced_type = ccg_type.replace(substitution)
        """
        return CCGTypeAnnotation(self.type.replace(sigma), self.annot)
