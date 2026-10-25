(fn StrikeNpc (Attacker Target Atk Def DmgMin DmgMax Scale Crit Pen Bonus Flank Armour)
  (Funzionedichiamata|FlankBonus :Attacker Attacker :Target Target :Most Flank)
  (Funzionedichiamata|ResolveHit :Atk Atk :Def Def :DmgMin DmgMin :DmgMax DmgMax :Scale Scale :Crit Crit :Pen Pen :Bonus Bonus :Armour Armour)
  (Classe|BPDlgNPC|ThreatFromStrike Target :Attacker Attacker :Damage (Variabili|Predefinito|OttieniLastDamage))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) 0.0)
    (:then
      (Classe|BPDlgNPC|TakeHit Target (Variabili|Predefinito|OttieniLastDamage)))
    (:else
      (Classe|BPDlgNPC|MissFeedback Target))))
