(fn HitFoe (Bonus Mul bOff bSure)
  (Variabili|Predefinito|ImpostaHAtk (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniAttack) (Variabili|Predefinito|OttieniNOwnAtk)) Bonus) (Matematica|Float|SelectFloat 1000.0 0.0 bSure)))
  (Variabili|Predefinito|ImpostaHMin (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniNOffMin) (Variabili|Predefinito|OttieniDmgMin) bOff) Mul) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnScale) 1.0)))
  (Variabili|Predefinito|ImpostaHMax (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniNOffMax) (Variabili|Predefinito|OttieniDmgMax) bOff) Mul) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnScale) 1.0)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|StrikePlayer (Variabili|Predefinito|OttieniMgr) :Attacker (Variabili|Ottieniunriferimentoasestesso) :Atk (Variabili|Predefinito|OttieniHAtk) :DmgMin (Variabili|Predefinito|OttieniHMin) :DmgMax (Variabili|Predefinito|OttieniHMax) :Scale (Variabili|Predefinito|OttieniDmgScale) :Crit (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniCrit) (Variabili|Predefinito|OttieniNOwnCrit)) :Pen (Variabili|Predefinito|OttieniPen) :Bonus (Variabili|Predefinito|OttieniDmgBonus) :Flank (Variabili|Predefinito|OttieniFlank)))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniFoe))
        (:then
          (Funzionedichiamata|HitNpcFoe))))))
