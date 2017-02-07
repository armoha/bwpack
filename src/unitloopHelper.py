from eudplib import *


def EUDLoopUnit2():
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    ptr, epd = EUDCreateVariables(2)
    ptr << 0x59CCA8
    epd << EPD(0x59CCA8)
    if EUDLoopN()(1700):
        ptr2, epd2 = EUDCreateVariables(2)
        SetVariables([ptr2, epd2], [ptr, epd])
        # sprite가 NULL이면 없는 유닛으로 판단.
        EUDContinueIf(MemoryEPD(epd + (0x0C // 4), Exactly, 0))
        yield ptr, epd
        EUDSetContinuePoint()
        ptr += 336
        epd += 336 // 4
    EUDEndLoopN()
