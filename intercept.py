import math
import random as pyRandom
import sys
from cmu_graphics import *


def onAppStart(app):
  # Canvas dimensions
  app.width = 600
  app.height = 750
  app.stepsPerSecond = 60

  # Screen state management ('title', 'game', or 'shop')
  app.screen = 'title'

  # Color Palette (Cold War Military / Tactical Radar)
  app.bgDark = rgb(22, 30, 24)
  app.gridColor = rgb(38, 56, 42)
  app.accentRed = rgb(185, 35, 35)
  app.accentGold = rgb(212, 175, 55)
  app.btnNormal = rgb(42, 54, 44)
  app.btnHover = rgb(62, 82, 66)
  app.textLight = rgb(235, 235, 225)

  # Title Screen Buttons
  btnWidth = 220
  btnHeight = 52
  centerX = app.width / 2

  app.buttons = [
      {
          'id': 'start',
          'label': 'START GAME',
          'x': centerX - btnWidth / 2,
          'y': 400,
          'w': btnWidth,
          'h': btnHeight,
          'hovered': False,
      },
      {
          'id': 'shop',
          'label': 'HANGAR / SHOP',
          'x': centerX - btnWidth / 2,
          'y': 475,
          'w': btnWidth,
          'h': btnHeight,
          'hovered': False,
      },
      {
          'id': 'exit',
          'label': 'EXIT GAME',
          'x': centerX - btnWidth / 2,
          'y': 550,
          'w': btnWidth,
          'h': btnHeight,
          'hovered': False,
      },
  ]

  # --- HANGAR / SHOP DATA ---
  app.totalPoints = 0
  app.scoreBanked = False
  app.selectedJetIndex = 0
  app.shopMessage = 'SELECT AN AIRCRAFT OR UNLOCK NEXT TIER'

  # Jets listed in strict unlock order with updated prices, ammo, and loadouts
  app.jets = [
      {
          'name': 'A8 JUMPER',
          'price': 0,
          'unlocked': True,
          'bodyColor': rgb(95, 115, 95),
          'wingColor': rgb(70, 88, 70),
          'accentColor': rgb(212, 175, 55),
          'shape': 'harrier',
          'speedMult': 1.00,
          'moveSpeed': 6.0,
          'maxHealth': 100,
          'startMG': 300,
          'maxMG': 600,
          'primaryType': 'gunpods',
          'specialType': None,
          'specialName': 'NONE',
          'startSpecial': 0,
          'maxSpecial': 0,
      },
      {
          'name': 'FALCON 16',
          'price': 3500,
          'unlocked': False,
          'bodyColor': rgb(130, 140, 150),
          'wingColor': rgb(100, 110, 120),
          'accentColor': rgb(65, 135, 210),
          'shape': 'falcon',
          'speedMult': 1.12,
          'moveSpeed': 6.8,
          'maxHealth': 110,
          'startMG': 300,
          'maxMG': 600,
          'primaryType': 'mg',
          'specialType': 'rockets',
          'specialName': 'ROCKETS',
          'startSpecial': 16,
          'maxSpecial': 50,
      },
      {
          'name': 'COBRA 18',
          'price': 10000,
          'unlocked': False,
          'bodyColor': rgb(110, 125, 140),
          'wingColor': rgb(85, 98, 112),
          'accentColor': rgb(220, 160, 40),
          'shape': 'cobra',
          'speedMult': 1.20,
          'moveSpeed': 7.4,
          'maxHealth': 125,
          'startMG': 300,
          'maxMG': 600,
          'primaryType': 'mg',
          'specialType': 'guided',
          'specialName': 'GUIDED MSL',
          'startSpecial': 10,
          'maxSpecial': 30,
      },
      {
          'name': 'SUPER EAGLE 15',
          'price': 25000,
          'unlocked': False,
          'bodyColor': rgb(90, 98, 105),
          'wingColor': rgb(68, 75, 82),
          'accentColor': rgb(185, 35, 35),
          'shape': 'eagle',
          'speedMult': 1.32,
          'moveSpeed': 8.0,
          'maxHealth': 140,
          'startMG': 300,
          'maxMG': 600,
          'primaryType': 'mg',
          'specialType': 'quad_guided',
          'specialName': 'QUAD MSL',
          'startSpecial': 5,
          'maxSpecial': 15,
      },
      {
          'name': 'X22',
          'price': 55000,
          'unlocked': False,
          'bodyColor': rgb(65, 70, 78),
          'wingColor': rgb(48, 52, 58),
          'accentColor': rgb(90, 210, 110),
          'shape': 'x22',
          'speedMult': 1.45,
          'moveSpeed': 8.8,
          'maxHealth': 150,
          'startMG': 300,
          'maxMG': 600,
          'primaryType': 'laser',
          'specialType': 'cluster',
          'specialName': 'CLUSTER BOMB',
          'startSpecial': 6,
          'maxSpecial': 18,
      },
  ]

  # Enemy visual template (scaled-down hostile A8 Jumper)
  app.enemyJetVisual = {
      'bodyColor': rgb(165, 42, 42),
      'wingColor': rgb(120, 28, 28),
      'accentColor': rgb(235, 190, 50),
      'shape': 'harrier',
  }

  resetGame(app)


def resetGame(app):
  jet = app.jets[app.selectedJetIndex]

  # Track & Speed Settings
  app.baseSpeed = 4.0 * jet['speedMult']
  app.trackSpeed = app.baseSpeed
  app.trackOffset = 0
  app.gridSpacing = 50

  # Distance, Score & Health
  app.distance = 0.0
  app.lastSpeedMilestone = 0
  app.lastSpawnMilestone = 0
  app.destroyedObstacles = 0
  app.score = 0
  app.maxHealth = jet['maxHealth']
  app.health = app.maxHealth
  app.gameOver = False
  app.scoreBanked = False

  # Player Jet State
  app.playerX = app.width / 2
  app.playerY = app.height * 0.72
  app.playerRadius = 18
  app.playerMoveSpeed = jet['moveSpeed']

  # Weapons & Ammunition
  app.mgAmmo = jet['startMG']
  app.maxMgAmmo = jet['maxMG']
  app.specialAmmo = jet['startSpecial']
  app.maxSpecialAmmo = jet['maxSpecial']
  app.primaryCooldown = 0
  app.specialCooldown = 0
  app.laserBeamTimer = 0
  app.laserBeamX = app.playerX

  # Entities & Projectiles
  app.enemies = []
  app.playerBullets = []
  app.enemyBullets = []
  app.specialProjectiles = []
  app.clusterSubmunitions = []
  app.explosions = []
  app.crates = []

  # Timers (spawnInterval shrinks every 200 distance units)
  app.spawnTimer = 0
  app.spawnInterval = 52
  app.crateTimer = 0
  app.crateInterval = 175


# --- Main Drawing Router ---


def redrawAll(app):
  if app.screen == 'title':
    drawTitleScreen(app)
  elif app.screen == 'game':
    drawGameScreen(app)
  elif app.screen == 'shop':
    drawShopScreen(app)


# --- Shared Radar Background & Pixel Jet Renderer ---


def drawRadarBackground(app):
  drawRect(0, 0, app.width, app.height, fill=app.bgDark)

  for x in range(0, app.width, 40):
    drawLine(x, 0, x, app.height, fill=app.gridColor, lineWidth=1)
  for y in range(0, app.height, 40):
    drawLine(0, y, app.width, y, fill=app.gridColor, lineWidth=1)

  radarCenterY = 230
  for radius in (90, 170, 250):
    drawCircle(
        app.width / 2,
        radarCenterY,
        radius,
        fill=None,
        border=app.gridColor,
        borderWidth=2,
    )

  drawLine(
      app.width / 2, 0, app.width / 2, app.height, fill=app.gridColor, lineWidth=1
  )


def drawPixelJet(cx, cy, jet, scale=1.0, facingDown=False):
  # Top-down pixel-styled 2D fighter jet (supports upward or downward orientation)
  d = -1 if facingDown else 1
  p = 5 * scale
  body = jet['bodyColor']
  wing = jet['wingColor']
  accent = jet['accentColor']
  cockpit = rgb(140, 220, 240)
  exhaust = rgb(255, 130, 30)

  def pxRect(xOff, yOff, wUnits, hUnits, color):
    w = wUnits * p
    h = hUnits * p
    x = cx + xOff * p
    if d == 1:
      y = cy + yOff * p
    else:
      y = cy - (yOff + hUnits) * p
    drawRect(x, y, w, h, fill=color)

  # Swept Wings
  if jet['shape'] == 'harrier':
    pxRect(-5, -1, 10, 2.5, wing)
    pxRect(-3.5, -2, 7, 1.5, wing)
  elif jet['shape'] == 'falcon':
    pxRect(-5.5, 0, 11, 2, wing)
    pxRect(-3.5, -1.5, 7, 1.5, wing)
  elif jet['shape'] == 'cobra':
    pxRect(-6, 0, 12, 2, wing)
    pxRect(-4, -1.5, 8, 1.5, wing)
    pxRect(-6.2, -1, 0.6, 3.5, accent)
    pxRect(5.6, -1, 0.6, 3.5, accent)
  elif jet['shape'] == 'eagle':
    pxRect(-6, -0.5, 12, 3, wing)
    pxRect(-4, -2, 8, 1.5, wing)
  elif jet['shape'] == 'x22':
    pxRect(-6.5, 0, 13, 2, wing)
    pxRect(-4.5, -1.5, 9, 1.5, wing)
    pxRect(-3, 2, 6, 1.2, wing)

  # Rear Horizontal Stabilizers
  pxRect(-3, 3.5, 6, 1.5, wing)

  # Central Fuselage & Nose Cone
  pxRect(-1.2, -4, 2.4, 8.5, body)
  pxRect(-0.8, -5.5, 1.6, 1.5, body)
  pxRect(-0.4, -6.5, 0.8, 1.0, accent)

  # Pixel Canopy (Cockpit)
  pxRect(-0.6, -2.8, 1.2, 2.2, cockpit)

  # Wing Accent Stripes
  pxRect(-4.5, 0.5, 1.5, 0.8, accent)
  pxRect(3.0, 0.5, 1.5, 0.8, accent)

  # Engine Afterburner Glow
  if jet['shape'] in ('cobra', 'eagle', 'x22'):
    pxRect(-1.1, 4.5, 0.8, 1.2, exhaust)
    pxRect(0.3, 4.5, 0.8, 1.2, exhaust)
  else:
    pxRect(-0.6, 4.5, 1.2, 1.2, exhaust)


# --- Title Screen ---


def drawTitleScreen(app):
  drawRadarBackground(app)

  # Radar sweep line and decorative blips
  radarCenterY = 230
  drawLine(
      app.width / 2,
      radarCenterY,
      app.width / 2 + 210,
      radarCenterY - 210,
      fill=rgb(55, 110, 65),
      lineWidth=2,
  )
  drawCircle(170, 160, 5, fill=app.accentRed)
  drawCircle(440, 290, 5, fill=app.accentRed)
  drawCircle(410, 140, 4, fill=app.accentRed, opacity=70)

  drawLabel(
      'TOP SECRET // AIRSPACE INTERCEPT',
      app.width / 2,
      145,
      size=13,
      font='monospace',
      bold=True,
      fill=app.accentGold,
  )

  drawLabel(
      'IRON CURTAIN',
      app.width / 2 + 3,
      203,
      size=52,
      font='monospace',
      bold=True,
      fill='black',
  )
  drawLabel(
      'IRON CURTAIN',
      app.width / 2,
      200,
      size=52,
      font='monospace',
      bold=True,
      fill=app.textLight,
  )

  drawLabel(
      'INTERCEPT',
      app.width / 2 + 3,
      258,
      size=48,
      font='monospace',
      bold=True,
      fill='black',
  )
  drawLabel(
      'INTERCEPT',
      app.width / 2,
      255,
      size=48,
      font='monospace',
      bold=True,
      fill=app.accentRed,
  )

  drawStar(
      app.width / 2,
      320,
      18,
      5,
      fill=app.accentRed,
      border=app.accentGold,
      borderWidth=1.5,
  )

  for btn in app.buttons:
    fillColor = app.btnHover if btn['hovered'] else app.btnNormal
    borderColor = app.accentGold if btn['hovered'] else app.textLight

    drawRect(btn['x'] + 4, btn['y'] + 4, btn['w'], btn['h'], fill='black')
    drawRect(
        btn['x'],
        btn['y'],
        btn['w'],
        btn['h'],
        fill=fillColor,
        border=borderColor,
        borderWidth=2,
    )
    drawLabel(
        btn['label'],
        btn['x'] + btn['w'] / 2,
        btn['y'] + btn['h'] / 2,
        size=18,
        font='monospace',
        bold=True,
        fill=app.textLight,
    )


# --- Hangar / Shop Screen ---


def bankRunScore(app):
  if not app.scoreBanked:
    app.totalPoints += app.score
    app.scoreBanked = True


def getShopCardBounds(app, index):
  cardW = 168
  cardH = 212
  gapX = 20
  gapY = 20
  startY = 140

  if index < 3:
    rowWidth = 3 * cardW + 2 * gapX
    startX = (app.width - rowWidth) / 2
    x = startX + index * (cardW + gapX)
    y = startY
  else:
    rowWidth = 2 * cardW + gapX
    startX = (app.width - rowWidth) / 2
    x = startX + (index - 3) * (cardW + gapX)
    y = startY + cardH + gapY

  return x, y, cardW, cardH


def drawShopScreen(app):
  drawRadarBackground(app)

  drawLabel(
      'AIRCRAFT HANGAR // ARMORY',
      app.width / 2,
      42,
      size=26,
      font='monospace',
      bold=True,
      fill=app.textLight,
  )

  drawRect(
      app.width / 2 - 155,
      66,
      310,
      32,
      fill=rgb(15, 22, 17),
      border=app.accentGold,
      borderWidth=1.5,
  )
  drawLabel(
      f'TOTAL POINTS: {app.totalPoints} PTS',
      app.width / 2,
      82,
      size=15,
      font='monospace',
      bold=True,
      fill=app.accentGold,
  )

  drawLabel(
      app.shopMessage,
      app.width / 2,
      118,
      size=12,
      font='monospace',
      bold=True,
      fill=rgb(140, 210, 150),
  )

  nextUnlockIndex = None
  for i, j in enumerate(app.jets):
    if not j['unlocked']:
      nextUnlockIndex = i
      break

  for i, jet in enumerate(app.jets):
    x, y, w, h = getShopCardBounds(app, i)
    isEquipped = i == app.selectedJetIndex
    isNextToUnlock = i == nextUnlockIndex

    if isEquipped:
      cardFill = rgb(36, 56, 40)
      borderCol = rgb(90, 210, 110)
      borderW = 3
    elif jet['unlocked']:
      cardFill = rgb(32, 42, 34)
      borderCol = app.textLight
      borderW = 2
    elif isNextToUnlock:
      cardFill = rgb(28, 34, 30)
      borderCol = app.accentGold
      borderW = 2
    else:
      cardFill = rgb(20, 24, 21)
      borderCol = rgb(75, 80, 75)
      borderW = 1.5

    drawRect(x + 4, y + 4, w, h, fill='black', opacity=70)
    drawRect(x, y, w, h, fill=cardFill, border=borderCol, borderWidth=borderW)

    # Aircraft Name
    drawLabel(
        jet['name'],
        x + w / 2,
        y + 19,
        size=13,
        font='monospace',
        bold=True,
        fill=app.textLight if jet['unlocked'] else rgb(160, 160, 155),
    )

    # Pixel Jet Icon
    drawPixelJet(x + w / 2, y + 78, jet, scale=1.05)

    # Loadout & Speed Summary
    priLabel = (
        '3X GUNPODS'
        if jet['primaryType'] == 'gunpods'
        else ('LASER' if jet['primaryType'] == 'laser' else 'MG')
    )
    specLabel = (
        f"{jet['specialName']} ({jet['startSpecial']})"
        if jet['specialType']
        else 'NO SPECIAL'
    )
    drawLabel(
        f"SPD:{int(jet['speedMult']*100)}% | {priLabel}",
        x + w / 2,
        y + 128,
        size=9,
        font='monospace',
        bold=True,
        fill=rgb(190, 210, 195),
    )
    drawLabel(
        specLabel,
        x + w / 2,
        y + 142,
        size=9,
        font='monospace',
        bold=True,
        fill=app.accentGold,
    )

    if not jet['unlocked']:
      drawRect(x + 14, y + 36, w - 28, 76, fill='black', opacity=45)
      lockTag = 'NEXT UNLOCK' if isNextToUnlock else 'LOCKED'
      tagColor = app.accentGold if isNextToUnlock else app.accentRed
      drawLabel(
          lockTag,
          x + w / 2,
          y + 74,
          size=11,
          font='monospace',
          bold=True,
          fill=tagColor,
      )

    # Price Tag / Status Box below icon & specs
    tagY = y + 164
    drawRect(
        x + 14,
        tagY,
        w - 28,
        30,
        fill=rgb(15, 20, 16),
        border=borderCol,
        borderWidth=1,
    )

    if isEquipped:
      statusText = 'EQUIPPED'
      statusColor = rgb(90, 210, 110)
    elif jet['unlocked']:
      statusText = 'CLICK TO EQUIP'
      statusColor = app.textLight
    else:
      statusText = f"{jet['price']} PTS"
      statusColor = (
          app.accentGold if app.totalPoints >= jet['price'] else app.accentRed
      )

    drawLabel(
        statusText,
        x + w / 2,
        tagY + 15,
        size=12,
        font='monospace',
        bold=True,
        fill=statusColor,
    )

  # Back to Title Button
  backX, backY, backW, backH = app.width / 2 - 110, 650, 220, 46
  drawRect(backX + 4, backY + 4, backW, backH, fill='black')
  drawRect(
      backX,
      backY,
      backW,
      backH,
      fill=app.btnNormal,
      border=app.accentGold,
      borderWidth=2,
  )
  drawLabel(
      'BACK TO MENU',
      backX + backW / 2,
      backY + backH / 2,
      size=16,
      font='monospace',
      bold=True,
      fill=app.textLight,
  )


# --- Gameplay Screen ---


def drawGameScreen(app):
  jet = app.jets[app.selectedJetIndex]

  # 1. Cold War Scrolling Tactical Track Background
  drawRect(0, 0, app.width, app.height, fill=app.bgDark)

  for x in range(0, app.width + 1, app.gridSpacing):
    drawLine(x, 0, x, app.height, fill=app.gridColor, lineWidth=1)

  drawLine(6, 0, 6, app.height, fill=app.accentGold, lineWidth=3)
  drawLine(
      app.width - 6, 0, app.width - 6, app.height, fill=app.accentGold, lineWidth=3
  )

  y = app.trackOffset - app.gridSpacing
  while y < app.height:
    drawLine(0, y, app.width, y, fill=app.gridColor, lineWidth=1)
    y += app.gridSpacing

  # Upper 1/5 enemy spawn zone line
  spawnZoneY = app.height / 5
  drawLine(
      0,
      spawnZoneY,
      app.width,
      spawnZoneY,
      fill=rgb(70, 45, 45),
      lineWidth=1,
      dashes=True,
  )

  # 2. Supply Crates & Repair Kits (Enlarged size & hitbox)
  for crate in app.crates:
    cx, cy, r = crate['x'], crate['y'], crate['r']
    if crate['type'] == 'mg':
      boxColor = rgb(60, 120, 75)
      trimColor = rgb(160, 240, 170)
      tag = 'MG'
    elif crate['type'] == 'special':
      boxColor = rgb(140, 100, 35)
      trimColor = app.accentGold
      tag = 'SP'
    else:
      boxColor = rgb(150, 45, 45)
      trimColor = app.textLight
      tag = '+HP'

    drawRect(
        cx - r,
        cy - r,
        r * 2,
        r * 2,
        fill=boxColor,
        border=trimColor,
        borderWidth=2.5,
    )
    drawLabel(
        tag, cx, cy, size=11, font='monospace', bold=True, fill=app.textLight
    )

  # 3. X22 Laser Beam Effect
  if app.laserBeamTimer > 0:
    drawLine(
        app.laserBeamX,
        0,
        app.laserBeamX,
        app.playerY - 20,
        fill=rgb(90, 255, 140),
        lineWidth=10,
        opacity=45,
    )
    drawLine(
        app.laserBeamX,
        0,
        app.laserBeamX,
        app.playerY - 20,
        fill=rgb(210, 255, 225),
        lineWidth=4,
    )

  # 4. Player Bullets & Special Projectiles
  for b in app.playerBullets:
    drawRect(b['x'] - 2, b['y'] - 6, 4, 12, fill=rgb(255, 235, 110))

  for sp in app.specialProjectiles:
    if sp['type'] == 'rocket':
      drawRect(sp['x'] - 3, sp['y'] - 8, 6, 16, fill=rgb(255, 140, 40))
      drawCircle(sp['x'], sp['y'] + 9, 3, fill=rgb(255, 220, 120))
    elif sp['type'] == 'cluster':
      # Heavy cluster canister
      drawRect(
          sp['x'] - 5,
          sp['y'] - 9,
          10,
          18,
          fill=rgb(90, 190, 110),
          border=app.accentGold,
          borderWidth=1.5,
      )
      drawCircle(sp['x'], sp['y'] + 10, 4, fill=rgb(160, 255, 180))
    else:
      # Guided missile
      drawRect(sp['x'] - 3, sp['y'] - 9, 6, 18, fill=rgb(110, 210, 255))
      drawCircle(sp['x'], sp['y'] + 10, 3.5, fill=rgb(255, 120, 50))

  # Cluster Submunitions (scattered bomblets before 0.2s detonation)
  for sub in app.clusterSubmunitions:
    drawCircle(
        sub['x'],
        sub['y'],
        4.5,
        fill=rgb(255, 175, 45),
        border=app.accentRed,
        borderWidth=1,
    )

  # 5. Enemy Machinegun Rounds
  for eb in app.enemyBullets:
    drawCircle(eb['x'], eb['y'], 3.5, fill=rgb(255, 70, 70))

  # 6. Hostile Jets (Scaled-down hostile A8 Jumpers, HP = 1)
  for enemy in app.enemies:
    drawPixelJet(
        enemy['x'],
        enemy['y'],
        app.enemyJetVisual,
        scale=0.68,
        facingDown=True,
    )

  # 7. Player Equipped Fighter Jet
  drawPixelJet(app.playerX, app.playerY, jet, scale=0.92, facingDown=False)

  # 8. Explosion Blast Rings
  for exp in app.explosions:
    progress = exp['timer'] / exp['maxTimer']
    curRadius = exp['maxRadius'] * progress
    alpha = max(10, int(90 * (1 - progress)))
    drawCircle(
        exp['x'],
        exp['y'],
        curRadius,
        fill=rgb(255, 140, 40),
        border=app.accentGold,
        borderWidth=2,
        opacity=alpha,
    )

  # 9. Upper-Left HUD (Score, Health %, MG Ammo, Special Ammo)
  healthPct = int((app.health / app.maxHealth) * 100)
  healthColor = (
      rgb(90, 210, 110)
      if healthPct > 50
      else (app.accentGold if healthPct > 25 else app.accentRed)
  )

  drawRect(
      12,
      12,
      245,
      126,
      fill=rgb(15, 22, 17),
      border=app.accentGold,
      borderWidth=1.5,
      opacity=88,
  )
  drawLabel(
      f'SCORE: {app.score}',
      22,
      28,
      size=14,
      font='monospace',
      bold=True,
      fill=app.textLight,
      align='left',
  )
  drawLabel(
      f'HEALTH: {healthPct}%',
      22,
      49,
      size=14,
      font='monospace',
      bold=True,
      fill=healthColor,
      align='left',
  )

  mgLabel = 'LASER CHG' if jet['primaryType'] == 'laser' else 'MG ROUNDS'
  mgColor = app.accentRed if app.mgAmmo <= 50 else rgb(160, 235, 175)
  drawLabel(
      f'{mgLabel}: {app.mgAmmo}/{app.maxMgAmmo}',
      22,
      70,
      size=13,
      font='monospace',
      bold=True,
      fill=mgColor,
      align='left',
  )

  if jet['specialType']:
    spColor = app.accentGold if app.specialAmmo > 0 else rgb(150, 150, 150)
    drawLabel(
        f"{jet['specialName']}: {app.specialAmmo}/{app.maxSpecialAmmo}",
        22,
        91,
        size=13,
        font='monospace',
        bold=True,
        fill=spColor,
        align='left',
    )
    ctrlHint = '[SPACE] FIRE  [E] SPECIAL'
  else:
    drawLabel(
        'SPECIAL: NONE (3X GUNPODS)',
        22,
        91,
        size=12,
        font='monospace',
        bold=True,
        fill=rgb(150, 160, 155),
        align='left',
    )
    ctrlHint = '[SPACE] FIRE GUNPODS'

  drawLabel(
      ctrlHint,
      22,
      115,
      size=11,
      font='monospace',
      bold=True,
      fill=app.accentGold,
      align='left',
  )

  # 10. Game Over Overlay
  if app.gameOver:
    drawRect(0, 0, app.width, app.height, fill='black', opacity=65)
    drawRect(
        app.width / 2 - 185,
        app.height / 2 - 95,
        370,
        190,
        fill=app.bgDark,
        border=app.accentRed,
        borderWidth=3,
    )
    drawLabel(
        'AIRCRAFT DESTROYED',
        app.width / 2,
        app.height / 2 - 50,
        size=24,
        font='monospace',
        bold=True,
        fill=app.accentRed,
    )
    drawLabel(
        f'FINAL SCORE: {app.score}',
        app.width / 2,
        app.height / 2 - 12,
        size=18,
        font='monospace',
        bold=True,
        fill=app.textLight,
    )
    drawLabel(
        f'BANKED TOTAL: {app.totalPoints} PTS',
        app.width / 2,
        app.height / 2 + 18,
        size=14,
        font='monospace',
        bold=True,
        fill=app.accentGold,
    )
    drawLabel(
        'Press R to Restart or ESC for Menu',
        app.width / 2,
        app.height / 2 + 56,
        size=13,
        font='monospace',
        fill=app.textLight,
    )


# --- Game Loop & Combat Mechanics ---


def onStep(app):
  if app.screen != 'game' or app.gameOver:
    return

  jet = app.jets[app.selectedJetIndex]

  # Cooldown timers
  if app.primaryCooldown > 0:
    app.primaryCooldown -= 1
  if app.specialCooldown > 0:
    app.specialCooldown -= 1
  if app.laserBeamTimer > 0:
    app.laserBeamTimer -= 1
    app.laserBeamX = app.playerX

  # 1. Scroll the track downward
  app.trackOffset = (app.trackOffset + app.trackSpeed) % app.gridSpacing

  # 2. Update distance & scale track speed by +1% every 100 units
  app.distance += app.trackSpeed * 0.25
  currentMilestone = int(app.distance // 100)
  if currentMilestone > app.lastSpeedMilestone and app.distance <= 15000:
    app.trackSpeed *= 1.01
    app.lastSpeedMilestone = currentMilestone

  # 3. Increase enemy spawn rate every 200 units traveled
  currentSpawnMilestone = int(app.distance // 200)
  if currentSpawnMilestone > app.lastSpawnMilestone:
    app.spawnInterval = max(14, int(app.spawnInterval * 0.90))
    app.lastSpawnMilestone = currentSpawnMilestone

  # 4. Update total score
  app.score = int(app.distance) + app.destroyedObstacles

  # 5. Spawn enemies on the upper 1/5 of the screen
  app.spawnTimer += 1
  if app.spawnTimer >= app.spawnInterval:
    spawnEnemy(app)
    app.spawnTimer = 0

  # 6. Spawn random supply crates / repair kits
  app.crateTimer += 1
  if app.crateTimer >= app.crateInterval:
    spawnCrate(app)
    app.crateTimer = 0

  # 7. Move player machinegun bullets
  activePlayerBullets = []
  for b in app.playerBullets:
    b['x'] += b['vx']
    b['y'] += b['vy']
    if 0 <= b['x'] <= app.width and b['y'] >= -15:
      activePlayerBullets.append(b)
  app.playerBullets = activePlayerBullets

  # 8. Move special projectiles (Unguided Rockets, Guided Missiles, Cluster Bombs)
  activeSpecials = []
  for sp in app.specialProjectiles:
    if sp['type'] in ('rocket', 'cluster'):
      sp['y'] += sp['vy']
      sp['traveled'] += abs(sp['vy'])
      if sp['traveled'] >= sp['maxRange'] or sp['y'] <= 15:
        if sp['type'] == 'rocket':
          triggerBlast(app, sp['x'], sp['y'], radius=75)
        else:
          detonateClusterBomb(app, sp['x'], sp['y'])
      else:
        activeSpecials.append(sp)

    elif sp['type'] == 'guided':
      # Home in on nearest enemy on screen
      target = findNearestEnemy(app, sp['x'], sp['y'])
      if target is not None:
        dx = target['x'] - sp['x']
        dy = target['y'] - sp['y']
        dist = math.hypot(dx, dy)
        if dist > 0:
          desiredVx = (dx / dist) * sp['speed']
          desiredVy = (dy / dist) * sp['speed']
          sp['vx'] = sp['vx'] * 0.84 + desiredVx * 0.16
          sp['vy'] = sp['vy'] * 0.84 + desiredVy * 0.16
      sp['x'] += sp['vx']
      sp['y'] += sp['vy']
      sp['life'] -= 1
      if sp['life'] > 0 and -20 <= sp['x'] <= app.width + 20 and sp['y'] >= -20:
        activeSpecials.append(sp)
  app.specialProjectiles = activeSpecials

  # 9. Update scattered Cluster Submunitions (~0.2s = 12 frames at 60 FPS)
  activeSubmunitions = []
  for sub in app.clusterSubmunitions:
    sub['x'] += sub['vx']
    sub['y'] += sub['vy']
    sub['timer'] -= 1
    if sub['timer'] <= 0:
      triggerBlast(app, sub['x'], sub['y'], radius=48)
    else:
      activeSubmunitions.append(sub)
  app.clusterSubmunitions = activeSubmunitions

  # 10. Move enemy machinegun bullets & check player hits
  activeEnemyBullets = []
  for eb in app.enemyBullets:
    eb['x'] += eb['vx']
    eb['y'] += eb['vy']
    if math.hypot(eb['x'] - app.playerX, eb['y'] - app.playerY) <= (
        app.playerRadius + 3
    ):
      damagePlayer(app, 8)
    elif 0 <= eb['x'] <= app.width and eb['y'] <= app.height + 15:
      activeEnemyBullets.append(eb)
  app.enemyBullets = activeEnemyBullets

  # 11. Move crates & check player pickup (enlarged hitbox)
  activeCrates = []
  for crate in app.crates:
    crate['y'] += app.trackSpeed
    if math.hypot(crate['x'] - app.playerX, crate['y'] - app.playerY) <= (
        app.playerRadius + crate['r'] + 6
    ):
      applyCratePickup(app, crate)
    elif crate['y'] - crate['r'] <= app.height:
      activeCrates.append(crate)
  app.crates = activeCrates

  # 12. Update enemies, firing, and projectile collisions (Enemy HP = 1)
  remainingEnemies = []
  for enemy in app.enemies:
    enemy['y'] += app.trackSpeed + enemy['extraSpeed']

    # Enemy single-barrel machinegun fire
    enemy['fireTimer'] -= 1
    if enemy['fireTimer'] <= 0 and enemy['y'] < app.playerY - 40:
      fireEnemyMachinegun(app, enemy)
      enemy['fireTimer'] = pyRandom.randint(55, 95)

    # Check player MG bullet hits
    for b in list(app.playerBullets):
      if math.hypot(b['x'] - enemy['x'], b['y'] - enemy['y']) <= (
          enemy['r'] + 5
      ):
        enemy['hp'] -= 1
        app.playerBullets.remove(b)
        break

    # Check special projectile direct impacts
    for sp in list(app.specialProjectiles):
      if math.hypot(sp['x'] - enemy['x'], sp['y'] - enemy['y']) <= (
          enemy['r'] + 10
      ):
        if sp['type'] == 'rocket':
          triggerBlast(app, sp['x'], sp['y'], radius=75)
        elif sp['type'] == 'cluster':
          detonateClusterBomb(app, sp['x'], sp['y'])
        else:
          enemy['hp'] -= 1
          triggerBlast(app, sp['x'], sp['y'], radius=32)
        app.specialProjectiles.remove(sp)
        break

    if enemy['hp'] <= 0:
      app.destroyedObstacles += 25
      app.explosions.append({
          'x': enemy['x'],
          'y': enemy['y'],
          'maxRadius': 26,
          'timer': 1,
          'maxTimer': 12,
      })
      continue

    # Check direct mid-air collision with player jet
    if (
        math.hypot(app.playerX - enemy['x'], app.playerY - enemy['y'])
        <= app.playerRadius + enemy['r']
    ):
      damagePlayer(app, 25)
      app.explosions.append({
          'x': enemy['x'],
          'y': enemy['y'],
          'maxRadius': 30,
          'timer': 1,
          'maxTimer': 14,
      })
      continue

    if enemy['y'] - enemy['r'] <= app.height:
      remainingEnemies.append(enemy)

  app.enemies = remainingEnemies

  # 13. Advance explosion animations
  activeExplosions = []
  for exp in app.explosions:
    exp['timer'] += 1
    if exp['timer'] <= exp['maxTimer']:
      activeExplosions.append(exp)
  app.explosions = activeExplosions


def damagePlayer(app, amount):
  if app.gameOver:
    return
  app.health = max(0, app.health - amount)
  if app.health <= 0:
    app.gameOver = True
    bankRunScore(app)


def spawnEnemy(app):
  enemyRadius = 15
  # Random X across screen width, random Y within upper 1/5 of screen
  randX = pyRandom.randint(enemyRadius + 8, app.width - enemyRadius - 8)
  randY = pyRandom.randint(enemyRadius, max(enemyRadius + 1, int(app.height / 5)))

  app.enemies.append({
      'x': randX,
      'y': randY,
      'r': enemyRadius,
      'hp': 1,
      'extraSpeed': pyRandom.uniform(0.9, 2.1),
      'fireTimer': pyRandom.randint(25, 65),
  })


def spawnCrate(app):
  jet = app.jets[app.selectedJetIndex]
  pool = ['mg', 'repair']
  if jet['specialType'] is not None:
    pool.append('special')

  crateType = pyRandom.choice(pool)
  r = 18  # Slightly larger size and hitbox
  randX = pyRandom.randint(r + 14, app.width - r - 14)
  app.crates.append({'x': randX, 'y': -r, 'r': r, 'type': crateType})


def applyCratePickup(app, crate):
  if crate['type'] == 'mg':
    app.mgAmmo = min(app.maxMgAmmo, app.mgAmmo + 150)
  elif crate['type'] == 'special':
    app.specialAmmo = min(app.maxSpecialAmmo, app.specialAmmo + 4)
  elif crate['type'] == 'repair':
    app.health = min(app.maxHealth, app.health + 30)


def fireEnemyMachinegun(app, enemy):
  dx = app.playerX - enemy['x']
  dy = app.playerY - enemy['y']
  dist = math.hypot(dx, dy)
  bulletSpeed = app.trackSpeed + 4.5
  if dist > 0 and dy > 0:
    vx = (dx / dist) * (bulletSpeed * 0.45)
    vy = bulletSpeed
  else:
    vx = 0
    vy = bulletSpeed

  app.enemyBullets.append({'x': enemy['x'], 'y': enemy['y'] + 14, 'vx': vx, 'vy': vy})


def firePrimaryWeapon(app):
  jet = app.jets[app.selectedJetIndex]
  if app.primaryCooldown > 0 or app.mgAmmo <= 0:
    return

  if jet['primaryType'] == 'gunpods':
    # A8 Jumper: fires 3 spread bullets for 1 MG round
    app.mgAmmo -= 1
    app.primaryCooldown = 8
    for vx in (-1.6, 0.0, 1.6):
      app.playerBullets.append(
          {'x': app.playerX, 'y': app.playerY - 18, 'vx': vx, 'vy': -12.5}
      )

  elif jet['primaryType'] == 'mg':
    # Standard twin nose machinegun
    app.mgAmmo -= 1
    app.primaryCooldown = 6
    app.playerBullets.append(
        {'x': app.playerX - 5, 'y': app.playerY - 18, 'vx': 0, 'vy': -13.5}
    )
    app.playerBullets.append(
        {'x': app.playerX + 5, 'y': app.playerY - 18, 'vx': 0, 'vy': -13.5}
    )

  elif jet['primaryType'] == 'laser':
    # X22: high-energy vertical laser beam using 5 MG charge
    cost = min(app.mgAmmo, 5)
    app.mgAmmo -= cost
    app.primaryCooldown = 14
    app.laserBeamTimer = 6
    app.laserBeamX = app.playerX

    surviving = []
    for enemy in app.enemies:
      if (
          enemy['y'] < app.playerY
          and abs(enemy['x'] - app.playerX) <= enemy['r'] + 10
      ):
        app.destroyedObstacles += 25
        app.explosions.append({
            'x': enemy['x'],
            'y': enemy['y'],
            'maxRadius': 28,
            'timer': 1,
            'maxTimer': 12,
        })
      else:
        surviving.append(enemy)
    app.enemies = surviving


def fireSpecialWeapon(app):
  jet = app.jets[app.selectedJetIndex]
  if not jet['specialType'] or app.specialCooldown > 0 or app.specialAmmo <= 0:
    return

  app.specialAmmo -= 1
  app.specialCooldown = 22

  if jet['specialType'] == 'rockets':
    # Falcon 16: fast unguided rocket that detonates after traveling 320px
    app.specialProjectiles.append({
        'type': 'rocket',
        'x': app.playerX,
        'y': app.playerY - 20,
        'vx': 0,
        'vy': -11.5,
        'traveled': 0,
        'maxRange': 320,
    })

  elif jet['specialType'] == 'guided':
    # Cobra 18: single homing missile
    app.specialProjectiles.append({
        'type': 'guided',
        'x': app.playerX,
        'y': app.playerY - 20,
        'vx': 0,
        'vy': -9.5,
        'speed': 9.5,
        'life': 130,
    })

  elif jet['specialType'] == 'quad_guided':
    # Super Eagle 15: fires 4 homing missiles at once for 1 special ammo
    for xOff, vxInit in ((-18, -2.6), (-7, -0.9), (7, 0.9), (18, 2.6)):
      app.specialProjectiles.append({
          'type': 'guided',
          'x': app.playerX + xOff,
          'y': app.playerY - 16,
          'vx': vxInit,
          'vy': -9.2,
          'speed': 9.8,
          'life': 135,
      })

  elif jet['specialType'] == 'cluster':
    # X22: heavy cluster bomb that splits into a fixed 8-way bomblet ring
    app.specialProjectiles.append({
        'type': 'cluster',
        'x': app.playerX,
        'y': app.playerY - 20,
        'vx': 0,
        'vy': -10.5,
        'traveled': 0,
        'maxRange': 300,
    })


def detonateClusterBomb(app, cx, cy):
  # Primary cluster canister burst
  triggerBlast(app, cx, cy, radius=42)

  # Throw 8 submunitions in a fixed symmetrical pattern that detonate after 0.2s (12 frames)
  fixedPattern = [
      (0.0, -5.5),
      (3.9, -3.9),
      (5.5, 0.0),
      (3.9, 3.9),
      (0.0, 5.5),
      (-3.9, 3.9),
      (-5.5, 0.0),
      (-3.9, -3.9),
  ]
  for vx, vy in fixedPattern:
    app.clusterSubmunitions.append({
        'x': cx,
        'y': cy,
        'vx': vx,
        'vy': vy,
        'timer': 12,  # 12 frames at 60 FPS = 0.2 seconds
    })


def findNearestEnemy(app, x, y):
  nearest = None
  bestDist = 999999
  for enemy in app.enemies:
    d = math.hypot(enemy['x'] - x, enemy['y'] - y)
    if d < bestDist:
      bestDist = d
      nearest = enemy
  return nearest


def triggerBlast(app, bx, by, radius):
  app.explosions.append(
      {'x': bx, 'y': by, 'maxRadius': radius, 'timer': 1, 'maxTimer': 15}
  )
  surviving = []
  for enemy in app.enemies:
    if math.hypot(enemy['x'] - bx, enemy['y'] - by) <= radius + enemy['r']:
      app.destroyedObstacles += 25
    else:
      surviving.append(enemy)
  app.enemies = surviving


# --- User Input Handlers ---


def onKeyHold(app, keys):
  if app.screen != 'game' or app.gameOver:
    return

  if 'w' in keys or 'W' in keys:
    app.playerY = max(app.playerRadius + 8, app.playerY - app.playerMoveSpeed)
  if 's' in keys or 'S' in keys:
    app.playerY = min(
        app.height - app.playerRadius - 8, app.playerY + app.playerMoveSpeed
    )
  if 'a' in keys or 'A' in keys:
    app.playerX = max(app.playerRadius + 10, app.playerX - app.playerMoveSpeed)
  if 'd' in keys or 'D' in keys:
    app.playerX = min(
        app.width - app.playerRadius - 10, app.playerX + app.playerMoveSpeed
    )

  if 'space' in keys:
    firePrimaryWeapon(app)


def onKeyPress(app, key):
  if key == 'escape' and app.screen != 'title':
    if app.screen == 'game' and app.score > 0:
      bankRunScore(app)
    app.screen = 'title'
  elif (key == 'r' or key == 'R') and app.screen == 'game' and app.gameOver:
    resetGame(app)
  elif app.screen == 'game' and not app.gameOver:
    if key == 'space':
      firePrimaryWeapon(app)
    elif key in ('e', 'E', 'shift'):
      fireSpecialWeapon(app)


def onMouseMove(app, mouseX, mouseY):
  if app.screen != 'title':
    return

  for btn in app.buttons:
    btn['hovered'] = (
        btn['x'] <= mouseX <= btn['x'] + btn['w']
        and btn['y'] <= mouseY <= btn['y'] + btn['h']
    )


def onMousePress(app, mouseX, mouseY):
  if app.screen == 'title':
    for btn in app.buttons:
      if (
          btn['x'] <= mouseX <= btn['x'] + btn['w']
          and btn['y'] <= mouseY <= btn['y'] + btn['h']
      ):
        if btn['id'] == 'start':
          resetGame(app)
          app.screen = 'game'
        elif btn['id'] == 'shop':
          app.shopMessage = 'SELECT AN AIRCRAFT OR UNLOCK NEXT TIER'
          app.screen = 'shop'
        elif btn['id'] == 'exit':
          app.quit()
          sys.exit()

  elif app.screen == 'shop':
    backX, backY, backW, backH = app.width / 2 - 110, 650, 220, 46
    if backX <= mouseX <= backX + backW and backY <= mouseY <= backY + backH:
      app.screen = 'title'
      return

    nextUnlockIndex = None
    for i, j in enumerate(app.jets):
      if not j['unlocked']:
        nextUnlockIndex = i
        break

    for i, jet in enumerate(app.jets):
      x, y, w, h = getShopCardBounds(app, i)
      if x <= mouseX <= x + w and y <= mouseY <= y + h:
        if jet['unlocked']:
          app.selectedJetIndex = i
          app.shopMessage = f"EQUIPPED: {jet['name']}"
        elif i == nextUnlockIndex:
          if app.totalPoints >= jet['price']:
            app.totalPoints -= jet['price']
            jet['unlocked'] = True
            app.selectedJetIndex = i
            app.shopMessage = f"UNLOCKED & EQUIPPED: {jet['name']}!"
          else:
            needed = jet['price'] - app.totalPoints
            app.shopMessage = f'INSUFFICIENT POINTS (NEED {needed} MORE PTS)'
        else:
          prevName = app.jets[nextUnlockIndex]['name']
          app.shopMessage = f'UNLOCK {prevName} FIRST!'
        break


runApp()
