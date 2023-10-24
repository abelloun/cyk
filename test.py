
from CCGrammar import CCGrammar, CCGExprString, CCGTypeAtomic, CCGTypeComposite, Judgement
from CCGCKYParser import TypeRaisingLeft, ApplicationLeft, ApplicationRight


testJudg1 = Judgement(CCGExprString("hello"), CCGTypeComposite(
	1,
	CCGTypeAtomic("PHRASE"),
	CCGTypeAtomic("WORLD")
))

testJudg2 = Judgement(CCGExprString("world"), CCGTypeAtomic("WORLD"))

#~ print(ApplicationLeft.show())

#~ print(testJudg1.show())
#~ print(testJudg2.show())
r = TypeRaisingLeft.match([testJudg2])
#~ print(r.show())





#~ print("START")
z0 = ApplicationLeft.match([testJudg1, r])

print(z0.show())
