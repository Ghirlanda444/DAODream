(fn TakeStrike (Attacker InAttack InMin InMax InScale InCrit InPen InBonus InFlank)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Classe|BPPlotManager|StrikeNpc (Variabili|Predefinito|OttieniMgr) :Attacker Attacker :Target (Variabili|Ottieniunriferimentoasestesso) :Atk InAttack :Def (Variabili|Predefinito|OttieniDefense) :DmgMin InMin :DmgMax InMax :Scale InScale :Crit InCrit :Pen InPen :Bonus InBonus :Flank InFlank :Armour (Variabili|Predefinito|OttieniArmour)))))
