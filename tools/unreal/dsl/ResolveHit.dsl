(fn ResolveHit (Atk Def DmgMin DmgMax Scale Crit Pen Bonus Armour)
  (Variabili|Predefinito|ImpostaLastCombat (Utilità|Testo|GetGameTimeinSeconds))
  (Variabili|Predefinito|ImpostaLastCrit (Matematica|Booleano|ORBoolean (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Utility|Operatori|Moltiplica Crit (Utility|Operatori|Aggiungi (Utility|Operatori|Dividi (Variabili|Predefinito|OttieniLastFlank) 5.0) 1.0))) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniBackstab) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastFlank) 0.0)) (Variabili|Predefinito|OttieniStunStab))))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Utility|Operatori|Sottrai (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi Atk 54.0) (Variabili|Predefinito|OttieniLastFlank)) Def))
    (:then
      (Variabili|Predefinito|ImpostaHits (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniHits) 1))
      (Funzionedichiamata|RollHit :DmgMin DmgMin :DmgMax DmgMax :Scale Scale :Pen Pen :Bonus Bonus :Armour Armour))
    (:else
      (Variabili|Predefinito|ImpostaMisses (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniMisses) 1))
      (Variabili|Predefinito|ImpostaLastCrit "false")
      (Variabili|Predefinito|ImpostaLastDamage -1.0))))
