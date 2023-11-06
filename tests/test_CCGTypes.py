import unittest
from CCGTypes import CCGType, CCGTypeVar, CCGTypeAtomicVar, CCGTypeAtomic, CCGTypeComposite, CCGTypeAnnotation

class TestCCGTypes(unittest.TestCase):
    def test_ccg_type_var(self):
        # Create and test CCGTypeVar instances
        var1 = CCGTypeVar("X")
        var2 = CCGTypeVar("Y")

        self.assertEqual(var1.show(), "$X")
        self.assertEqual(var2.show(), "$Y")

    def test_ccg_type_atomic_var(self):
        # Create and test CCGTypeAtomicVar instances
        atomic_var1 = CCGTypeAtomicVar("X")
        atomic_var2 = CCGTypeAtomicVar("Y")

        self.assertEqual(atomic_var1.show(), "@X")
        self.assertEqual(atomic_var2.show(), "@Y")

    def test_ccg_type_atomic(self):
        # Create and test CCGTypeAtomic instances
        atomic_type1 = CCGTypeAtomic("N")
        atomic_type2 = CCGTypeAtomic("NP")

        self.assertEqual(atomic_type1.show(), "N")
        self.assertEqual(atomic_type2.show(), "NP")

    def test_ccg_type_composite(self):
        # Create and test CCGTypeComposite instances
        left_type = CCGTypeAtomic("NP")
        right_type = CCGTypeAtomic("N")

        composite_type1 = CCGTypeComposite(True, left_type, right_type)
        composite_type2 = CCGTypeComposite(False, left_type, right_type)

        self.assertEqual(composite_type1.show(), "(NP / N)")
        self.assertEqual(composite_type2.show(), "(NP \\ N)")

    def test_ccg_type_annotation(self):
        # Create and test CCGTypeAnnotation instances
        base_type1 = CCGTypeAtomic("NP")
        base_type2 = CCGTypeAtomic("N")
        annotation1 = "SBJ"
        annotation2 = "OBJ"

        annotation_type1 = CCGTypeAnnotation(base_type1, annotation1)
        annotation_type2 = CCGTypeAnnotation(base_type2, annotation2)

        self.assertEqual(annotation_type1.show(), "NP[SBJ]")
        self.assertEqual(annotation_type2.show(), "N[OBJ]")

    def test_ccg_type_unify(self):
        # Test CCGType unification
        t1 = CCGTypeAtomicVar("X")
        t2 = CCGTypeAtomicVar("Y")
        sigma = {}
        result = CCGType.unify(t1, t2, sigma)
        self.assertTrue(result)

        # Compare the attributes of the objects
        self.assertEqual(sigma["X"].name, "Y")

    def test_ccg_type_reset(self):
        CCGType.reset()
        t1 = CCGType.fresh("X")
        CCGType.reset()
        t2 = CCGType.fresh("X")
        self.assertEqual(t1, t2)
