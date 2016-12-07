# Algorithm by matbing(sksljh2091@naver.com)
# Pluginified by trgk(phu54321@naver.com)

from eudplib import *

cammoveLoc = GetLocationIndex('cammoveLoc')
inertia = int(settings.get('inertia', 5))
maxspeed = int(settings.get('maxspeed', 48))
target = GetLocationIndex(settings['targetloc'])

def onPluginStart():
    DoActions([
        SetMemory(0x58DC60 + 20 * cammoveLoc + 0x0, SetTo, 0),
        SetMemory(0x58DC60 + 20 * cammoveLoc + 0x4, SetTo, 0),
        SetMemory(0x58DC60 + 20 * cammoveLoc + 0x8, SetTo, 640),
        SetMemory(0x58DC60 + 20 * cammoveLoc + 0xC, SetTo, 384),
    ])


@EUDFunc
def sgnAbs(x):
    if EUDIf()(x >= 0x80000000):
        EUDReturn(-1, -x)
    if EUDElse()():
        EUDReturn(1, x)
    EUDEndIf()


def getTicks():
    return f_dwread_epd(EPD(0x57F23C))


lastTick = EUDVariable(-1)
scrollData = Db(52)


@EUDFunc
def afterTriggerExec():
    if EUDIf()(Memory(0x57F0B4, Exactly, 0)):
        EUDReturn()
    EUDEndIf()

    if EUDIf()([Switch('cammove', Set)]):
        currentTick = getTicks()
        if EUDIf()(lastTick == -1):  # Just started following
            lastTick << currentTick
        EUDEndIf()

        prevCamX = f_dwread_epd(EPD(0x62848C))
        prevCamY = f_dwread_epd(EPD(0x6284A8))

        DoActions(MoveLocation(cammoveLoc + 1, 'Map Revealer', P9, target + 1))
        locx = f_dwread_epd(EPD(0x58DC60 + 20 * cammoveLoc + 0x0))
        locy = f_dwread_epd(EPD(0x58DC60 + 20 * cammoveLoc + 0x4))

        if inertia == 0:
            dstx, dsty = locx, locy

        else:
            # We use fixed point arithmetics here
            fpQ = 256

            dx = (locx - prevCamX)
            dy = (locy - prevCamY)

            dstx, dsty = EUDCreateVariables(2)

            if EUDIf()([dx == 0, dy == 0]):
                dstx << locx
                dsty << locy

            if EUDElse()():
                dx_sgn, dxabs = sgnAbs(dx)
                dy_sgn, dyabs = sgnAbs(dy)

                dt = (currentTick - lastTick) * fpQ // 24

                # Calculating norm of vector (dx, dy), while preventing
                # potential overflows
                d = EUDVariable()
                if EUDIf()([dxabs <= 100, dyabs <= 100]):
                    d << f_sqrt(fpQ * fpQ * (dxabs * dxabs + dyabs * dyabs))
                if EUDElse()():
                    d << f_sqrt(fpQ * fpQ * (dxabs * dxabs + dyabs * dyabs))
                EUDEndIf()

                C = fpQ * fpQ // d
                newd = EUDVariable()
                newd << (fpQ * fpQ // (dt // inertia + C))
                if EUDIf()(d - newd >= maxspeed * fpQ):
                    newd << d - maxspeed * fpQ
                EUDEndIf()

                newdx, newdy = EUDCreateVariables(2)
                newdx = dxabs * (fpQ * fpQ) // d * newd // (fpQ * fpQ)
                newdy = dyabs * (fpQ * fpQ) // d * newd // (fpQ * fpQ)

                dstx << locx - dx_sgn * newdx
                dsty << locy - dy_sgn * newdy
            EUDEndIf()

        DoActions([
            SetCurrentPlayer(f_getuserplayerid()),
            SetMemory(0x58DC60 + 20 * cammoveLoc + 0x0, SetTo, dstx),
            SetMemory(0x58DC60 + 20 * cammoveLoc + 0x4, SetTo, dsty),
            SetMemory(0x58DC60 + 20 * cammoveLoc + 0x8, SetTo, dstx + 640),
            SetMemory(0x58DC60 + 20 * cammoveLoc + 0xC, SetTo, dsty + 384),
            CenterView(cammoveLoc + 1),
            SetMemory(0x62848C, SetTo, dstx),
            SetMemory(0x6284A8, SetTo, dsty)
        ])

        lastTick << currentTick

    if EUDElse()():
        if EUDIfNot()(lastTick == -1):
            lastTick << -1
        EUDEndIf()
    EUDEndIf()