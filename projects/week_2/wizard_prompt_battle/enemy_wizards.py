"""
Hard-coded list of available enemies for you to face
"""

from classes import EnemyWizard, Spell, Element, SpellType

ENEMY_WIZARDS = [
    EnemyWizard(
        name="Apex Drift Igniter",
        primary_element=Element.FIRE,
        secondary_element=Element.STORM,
        attack=0.87, defense=0.28, health=0.46, healing=0.18, arcane=0.64,
        spells=[
            Spell("Redline Shatter", SpellType.DAMAGE, "A screaming arc of heat snaps like a whip across the field.", Element.FIRE, 0.86),
            Spell("Turbo Spark Trail", SpellType.DAMAGE, "A zigzag of sparks lashes the ground and erupts beneath the foe.", Element.STORM, 0.72),
            Spell("Afterburn Veil", SpellType.BUFF, "A hot updraft wraps the caster, boosting acceleration and bite.", Element.FIRE, 0.58),
            Spell("Slipstream Stall", SpellType.DEBUFF, "A turbulent gust steals the enemy's momentum mid-charge.", Element.STORM, 0.63),
        ],
        combat_style="Glass-cannon sprinter who spikes early damage with risky, high-tempo bursts.",
        preview="Heat ripples off a restless frame; movements twitch toward sudden openings while the stance leaves a few edges unguarded."
    ),
    EnemyWizard(
        name="Kiln-Bound Bulwark",
        primary_element=Element.FIRE,
        secondary_element=Element.BALANCE,
        attack=0.62, defense=0.76, health=0.78, healing=0.32, arcane=0.48,
        spells=[
            Spell("Ceramic Carapace", SpellType.BUFF, "A kiln's glow hardens into plates that temper incoming blows.", Element.FIRE, 0.72),
            Spell("Coalbed Hammer", SpellType.DAMAGE, "Smoldering coals fuse into a heavy mace that slams down once.", Element.FIRE, 0.66),
            Spell("Equalize Emberline", SpellType.DEBUFF, "A thin ember-line redraws the field, sapping overextensions.", Element.BALANCE, 0.60),
            Spell("Hearth's Last Push", SpellType.DAMAGE, "A deep furnace cough hurls cinders in a compact blast.", Element.FIRE, 0.55),
        ],
        combat_style="Defensive bruiser who trades space for sustained, measured counters.",
        preview="A banked glow seeps from layered plating; their pace is unhurried, weight settling like a shield that rarely breaks rhythm."
    ),
    EnemyWizard(
        name="Glacier Thread Weaver",
        primary_element=Element.ICE,
        secondary_element=Element.MYTH,
        attack=0.46, defense=0.78, health=0.70, healing=0.34, arcane=0.72,
        spells=[
            Spell("Needle of Permafrost", SpellType.DAMAGE, "A hair-thin icicle stitches a precise seam through armor gaps.", Element.ICE, 0.64),
            Spell("Stillness Loom", SpellType.BUFF, "Silvery threads hush motion, tightening poise and guard.", Element.ICE, 0.68),
            Spell("Mirrored Sigil", SpellType.DEBUFF, "A reflective rune flips intent, dulling the foe's next gambit.", Element.MYTH, 0.62),
            Spell("Snowblind Parable", SpellType.DAMAGE, "A pale tale condenses as flurries that bite at exposed will.", Element.MYTH, 0.52),
        ],
        combat_style="Patient controller who pricks, slows, and redirects with surgical calm.",
        preview="Faint hoarfrost sketches careful lines; each motion measured, with strength kept in reserve for well-placed replies."
    ),
    EnemyWizard(
        name="Rimebreaker Vanguard",
        primary_element=Element.ICE,
        secondary_element=Element.BALANCE,
        attack=0.58, defense=0.84, health=0.82, healing=0.28, arcane=0.44,
        spells=[
            Spell("Glacial Ramline", SpellType.DAMAGE, "A wedge of blue ice bucks forward to shove the target off axis.", Element.ICE, 0.61),
            Spell("Braced Isotherm", SpellType.BUFF, "A stable temperature shell stiffens resolve and footing.", Element.BALANCE, 0.66),
            Spell("Fracture Timing", SpellType.DEBUFF, "Hairline cracks crawl underfoot, throwing rhythm out of step.", Element.ICE, 0.73),
            Spell("Sleet Hook", SpellType.DAMAGE, "A hooked slab skates low, sweeping legs in a cold snap.", Element.ICE, 0.49),
        ],
        combat_style="Tanky line-holder who wins ground inch by inch.",
        preview="Footfalls land like anchors; breath steams in steady columns, posture built to meet weight with weight."
    ),
    EnemyWizard(
        name="Tempest Crossfader",
        primary_element=Element.STORM,
        secondary_element=Element.MYTH,
        attack=0.83, defense=0.24, health=0.44, healing=0.20, arcane=0.77,
        spells=[
            Spell("Forked Drop", SpellType.DAMAGE, "A split bolt slams twice from mismatched angles.", Element.STORM, 0.88),
            Spell("Phase Crackle", SpellType.DEBUFF, "A static veil desyncs the foe's cues and timing.", Element.MYTH, 0.69),
            Spell("Capacitor Spinup", SpellType.BUFF, "Coiled charge hums under the skin, priming the next strike.", Element.STORM, 0.62),
            Spell("Whiplash Strobe", SpellType.DAMAGE, "Lightning strobes in a curt snap that stings and fades.", Element.STORM, 0.54),
        ],
        combat_style="All-in burst initiator who overwhelms with tempo spikes.",
        preview="Light flickers, timing stutters; the approach spikes like weather breaking faster than footing can hold."
    ),
    EnemyWizard(
        name="Gale Net Cartographer",
        primary_element=Element.STORM,
        secondary_element=Element.BALANCE,
        attack=0.60, defense=0.52, health=0.55, healing=0.26, arcane=0.68,
        spells=[
            Spell("Isobar Lash", SpellType.DAMAGE, "Pressure lines snap like cords that welt the target.", Element.STORM, 0.63),
            Spell("Crosswind Grid", SpellType.DEBUFF, "A lattice of gusts pens the foe into unfavorable lanes.", Element.BALANCE, 0.66),
            Spell("Trade-Wind Meter", SpellType.BUFF, "Reads the flow, easing casts and smoothing stance.", Element.STORM, 0.55),
            Spell("Cyclone Pincer", SpellType.DAMAGE, "Two small vortices converge, pinching from either flank.", Element.STORM, 0.57),
        ],
        combat_style="Map-maker tactician who shepherds foes into stormy traps.",
        preview="Drafts seem to map unseen lanes; pressure nudges rather than crushes, narrowing options one step at a time."
    ),
    EnemyWizard(
        name="Verdant Ward Alchemist",
        primary_element=Element.LIFE,
        secondary_element=Element.BALANCE,
        attack=0.44, defense=0.62, health=0.80, healing=0.86, arcane=0.58,
        spells=[
            Spell("Chlorophyll Surge", SpellType.DAMAGE, "Idk get attacked by chlorophyll nerd.", Element.LIFE, 0.82),
            Spell("Rootbound Brace", SpellType.BUFF, "Roots knit into greaves, steadying posture and guard.", Element.BALANCE, 0.61),
            Spell("Bramble Rebuke", SpellType.DAMAGE, "A crown of thorns snaps outward in a sudden ring.", Element.LIFE, 0.49),
            Spell("Pollen Lull", SpellType.DEBUFF, "Soft golden dust saps vigor and focus.", Element.LIFE, 0.67),
        ],
        combat_style="Sustain-heavy guardian who grinds through attrition and timely heals.",
        preview="The ground softens with quiet green; vigor lingers in their wake, edges muted by slow, steady renewal."
    ),
    EnemyWizard(
        name="Orchard Cutlass Corsair",
        primary_element=Element.LIFE,
        secondary_element=Element.FIRE,
        attack=0.70, defense=0.48, health=0.64, healing=0.52, arcane=0.50,
        spells=[
            Spell("Applewood Slash", SpellType.DAMAGE, "A curved blade of sweet smoke carves a bright arc.", Element.FIRE, 0.66),
            Spell("Sapling Rally", SpellType.BUFF, "Young shoots spring up, lending vigor to each motion.", Element.LIFE, 0.58),
            Spell("Cider Sting", SpellType.DEBUFF, "A tart spray stings eyes and dulls bite.", Element.LIFE, 0.55),
            Spell("Bonfire Grapnel", SpellType.DAMAGE, "A flaming hook snags and yanks the foe off balance.", Element.FIRE, 0.72),
        ],
        combat_style="Skirmishing duelist who mixes cuts with restorative beats.",
        preview="Sweet smoke and sparks trace quick arcs; footwork lively, with breath that steadies between swings."
    ),
    EnemyWizard(
        name="Pale Reliquary Pontiff",
        primary_element=Element.DEATH,
        secondary_element=Element.MYTH,
        attack=0.71, defense=0.50, health=0.52, healing=0.38, arcane=0.76,
        spells=[
            Spell("Ash Benediction", SpellType.DEBUFF, "A gray blessing leaves limbs leaden and hopes thin.", Element.DEATH, 0.74),
            Spell("Reliquary Spike", SpellType.DAMAGE, "A bone reliquary cracks open, firing a shard of loss.", Element.DEATH, 0.79),
            Spell("Procession of Echoes", SpellType.BUFF, "Ghostly choristers steady the caster's cadence.", Element.MYTH, 0.56),
            Spell("Catafalque Drop", SpellType.DAMAGE, "A shadow bier collapses forward in a crushing slide.", Element.DEATH, 0.66),
        ],
        combat_style="Pressure priest who withers and punctures in solemn rhythms.",
        preview="Gray motes orbit to a measured hymn; impacts linger, as if something is taken each time."
    ),
    EnemyWizard(
        name="Graveglass Cutpurse",
        primary_element=Element.DEATH,
        secondary_element=Element.ICE,
        attack=0.57, defense=0.64, health=0.60, healing=0.30, arcane=0.62,
        spells=[
            Spell("Funeral Filigree", SpellType.BUFF, "Cold etchings creep across armor, tightening seams shut.", Element.ICE, 0.63),
            Spell("Mournhook", SpellType.DAMAGE, "A hooked shadow tugs a piece of the foe's edge away.", Element.DEATH, 0.61),
            Spell("Last Breath Tax", SpellType.DEBUFF, "A toll is called at each inhale, skimming strength.", Element.DEATH, 0.72),
            Spell("Tombfrost Skewer", SpellType.DAMAGE, "A brittle spear of hoarfrost snaps and drives in.", Element.ICE, 0.58),
        ],
        combat_style="Attrition thief who chips, chills, and collects due.",
        preview="Air cools around close movements; small cuts add up, a chill settling in the joints."
    ),
    EnemyWizard(
        name="Labyrinth Stage Conjuror",
        primary_element=Element.MYTH,
        secondary_element=Element.STORM,
        attack=0.41, defense=0.44, health=0.50, healing=0.36, arcane=0.88,
        spells=[
            Spell("Curtain of Doubles", SpellType.BUFF, "Velvet folds part to reveal convincing stand-ins.", Element.MYTH, 0.74),
            Spell("Misdeal Reality", SpellType.DEBUFF, "Rules shuffle; the foe's sure thing turns sideways.", Element.MYTH, 0.77),
            Spell("Trapdoor Crescendo", SpellType.DAMAGE, "Floorboards drum, then vanish under a burst of light.", Element.STORM, 0.59),
            Spell("Wireframe Riddle", SpellType.DEBUFF, "A riddle binds in glowing lines that snag intent.", Element.MYTH, 0.68),
        ],
        combat_style="Trickster conductor who toys with expectations before the strike.",
        preview="Angles feel off by a hair; presence swells when you look away, as if the trick holds the charge."
    ),
    EnemyWizard(
        name="Cipher Mask Warden",
        primary_element=Element.MYTH,
        secondary_element=Element.BALANCE,
        attack=0.52, defense=0.58, health=0.62, healing=0.42, arcane=0.74,
        spells=[
            Spell("Glyph Lock", SpellType.DEBUFF, "A sigil clicks shut, jamming aggressive lines.", Element.MYTH, 0.71),
            Spell("Counterpoise Charm", SpellType.BUFF, "A measured charm sets stance square and steady.", Element.BALANCE, 0.60),
            Spell("Maskbreaker Feint", SpellType.DAMAGE, "A false opening invites a sharp, masked thrust.", Element.MYTH, 0.57),
            Spell("Evenhand Edict", SpellType.DEBUFF, "A calm decree dulls spikes and flattens surges.", Element.BALANCE, 0.65),
        ],
        combat_style="Control-leaning sentinel who edits the fight's terms.",
        preview="Clean lines flicker and fade; pressure arrives by degrees, the tempo tidied more than broken."
    ),
    EnemyWizard(
        name="Fulcrum Iron Magistrate",
        primary_element=Element.BALANCE,
        secondary_element=Element.FIRE,
        attack=0.60, defense=0.74, health=0.76, healing=0.38, arcane=0.58,
        spells=[
            Spell("Scaleside Rebuke", SpellType.DAMAGE, "A weighted strike lands at the pivot of overreach.", Element.BALANCE, 0.62),
            Spell("Counterweight Oath", SpellType.BUFF, "An oath steels posture and redistributes strain.", Element.BALANCE, 0.66),
            Spell("Verdict Spark", SpellType.DAMAGE, "A tight spark snaps from the gavel's invisible edge.", Element.FIRE, 0.55),
            Spell("Overrule", SpellType.DEBUFF, "A crisp motion voids the foe's advantage this turn.", Element.BALANCE, 0.70),
        ],
        combat_style="Methodical bruiser who punishes greed with tidy counters.",
        preview="Gestures fall in balanced beats; missteps feel heavier than hits, and momentum rarely strays for long."
    ),
    EnemyWizard(
        name="Ecliptic Arbor Arbiter",
        primary_element=Element.BALANCE,
        secondary_element=Element.LIFE,
        attack=0.48, defense=0.80, health=0.82, healing=0.46, arcane=0.60,
        spells=[
            Spell("Umbra Parry", SpellType.BUFF, "A crescent shade settles across guard and shoulder.", Element.BALANCE, 0.72),
            Spell("Radial Check", SpellType.DEBUFF, "Spokes of force arrest wild swings mid-arc.", Element.BALANCE, 0.68),
            Spell("Ringwood Strike", SpellType.DAMAGE, "A band of living wood tightens and snaps forward.", Element.LIFE, 0.57),
            Spell("Harmonic Push", SpellType.DAMAGE, "A gentle wave stacks into a sudden, centered shove.", Element.BALANCE, 0.60),
        ],
        combat_style="High-defense arbiter who shapes tempo and lanes.",
        preview="A dim ring turns with leaf-scented hush; efforts skid off in arcs as the pace drifts toward their center."
    )
]
