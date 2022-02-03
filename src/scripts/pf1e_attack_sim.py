import dice

DEBUG = False
FORCE_CRIT = False

class Weapon:
    n_dmg_dice = 0
    dmg_die = 'd0'
    attack_bonus = '+0'
    dmg_bonus = '+0'
    min_crit = 20
    crit_mult = 2
    finesse = False

    def __init__(self, n_dmg_dice, dmg_die, attack_bonus='+0', dmg_bonus='+0', min_crit=20, crit_mult=2, finesse=False):
        self.n_dmg_dice = n_dmg_dice
        self.dmg_die = dmg_die
        self.attack_bonus = attack_bonus
        self.dmg_bonus = dmg_bonus
        self.min_crit = min_crit
        self.crit_mult = crit_mult
        self.finesse = finesse


class Character:
    ac = 0
    mod_bab = 0
    mod_str = 0
    mod_dex = 0
    has_weapon_finesse = False


    def __init__(self, ac, mod_bab=0, mod_str=0, mod_dex=0, has_weapon_finesse=False):
        self.ac = ac
        self.mod_bab = mod_bab
        self.mod_str = mod_str
        self.mod_dex = mod_dex
        self.has_weapon_finesse = has_weapon_finesse

        global FORCE_CRIT

    def attack(self, weapon, target):
        """
        Outputs the damage done to the opponent (0 if miss)

        weapon - Weapon instance
        target - Character instance (just needs ac populated)
        """
        debug_log('attacking vs opponent with ac:', target.ac)

        raw_atk_roll = dice.roll('1d20')[0] if not FORCE_CRIT else 20

        # determine modifiers for attack roll
        atk_mod = self.mod_bab
        
        if self.has_weapon_finesse and weapon.finesse:
            debug_log('using dex mod for attack roll')
            atk_mod += self.mod_dex
        else:
            debug_log('using str mod for attack roll')
            atk_mod += self.mod_str

        # determine if attack misses, hits, or crits
        is_crit_fail = raw_atk_roll == 1
        is_crit_pass = raw_atk_roll >= weapon.min_crit

        debug_crit_msg = ''
        if is_crit_fail:
            debug_crit_msg = ' !!! CRIT FAIL !!!'
        elif is_crit_pass:
            debug_crit_msg = ' !!! CRIT PASS !!!'

        net_atk_roll = raw_atk_roll + atk_mod
        debug_log('attack: /r 1d20+{0} = {1}+{0} = {2}{3}'.format(atk_mod, raw_atk_roll, net_atk_roll, debug_crit_msg))

        is_hit = is_crit_pass or (not is_crit_fail and net_atk_roll >= target.ac)

        # if nat 1, auto-fail
        # if > ac, hit
        # if crit, auto-hit and roll to crit confirm
        # if nat 20, auto-hit and auto-crit confirm

        dmg = 0
        if is_hit:
            n_dmg_dice = weapon.n_dmg_dice

            # roll to confirm crit, adjust damage roll if cofirmed
            if is_crit_pass:
                if raw_atk_roll == 20:
                    is_crit_confirmed = True
                else:
                    crit_confirm_roll = '1d20+{}'.format(atk_mod)
                    crit_confirm_result = dice.roll(crit_confirm_roll)
                    is_crit_confirmed = crit_confirm_result >= target.ac
                    
                    debug_log('crit confirm: /r {} = {} ({})'.format(crit_confirm_roll, crit_confirm_result, 'confirms' if is_crit_confirmed else 'does not confirm'))
                
                # if crit confirms, double damage die
                if is_crit_confirmed:
                    n_dmg_dice = weapon.crit_mult * n_dmg_dice
            
            dmg_roll = '{0}{1}{2}+{3}'.format(n_dmg_dice, weapon.dmg_die, weapon.dmg_bonus, self.mod_str)

            dmg = dice.roll(dmg_roll)
            debug_log('damage: /r {0} = {1}'.format(dmg_roll, dmg))
        else:
            debug_log('miss!')
        
        debug_log('total damge:', dmg)
        return int(dmg)


def debug_log(*msg):
    if DEBUG:
        print(*msg)


if __name__ == '__main__':
    n_attacks = 10000

    pc = Character(ac=14, mod_bab=1, mod_str=2, mod_dex=2, has_weapon_finesse=True)
    opp = Character(ac=14)

    weapons = {
        'mwk_rapier':       Weapon(1, 'd6', attack_bonus='+1', dmg_bonus='+1', min_crit=18, finesse=True),
        'mwk_battleaxe':    Weapon(1, 'd8', attack_bonus='+1', dmg_bonus='+1', crit_mult=3),
        'mwk_heavy_pick':   Weapon(1, 'd6', attack_bonus='+1', dmg_bonus='+1', crit_mult=4)
    }

    weapon_tot_dmg = {w: 0 for w in weapons}

    print('simulating {} attacks for {} weapons...'.format(n_attacks, len(weapons.keys())))
    for n in range(n_attacks):
        for w in weapons.keys():
            weapon_tot_dmg[w] = weapon_tot_dmg[w] + pc.attack(weapons[w], opp) 

    for w in weapons.keys():
        print('{} avg dmg: {}'.format(w, weapon_tot_dmg[w]/n_attacks))

    # pc.attack(weapons['mwk_battleaxe'], opp)
