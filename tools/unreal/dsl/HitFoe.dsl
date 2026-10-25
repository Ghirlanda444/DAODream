(fn HitFoe (Bonus Mul bOff bSure)
  (Funzionedichiamata|ShootFx)
  (Variabili|Predefinito|ImpostaHAtk (Utility|Operatori|Sottrai (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniAttack) (Variabili|Predefinito|OttieniNOwnAtk)) Bonus) (Matematica|Float|SelectFloat 1000.0 0.0 bSure)) (Matematica|Float|SelectFloat (Matematica|Float|Max(Float) (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) (Variabili|Predefinito|OttieniFoe)) 100.0) (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniNRange) 8.0)) 0.0) 0.0 (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniNRange) 0.0))))
  (Variabili|Predefinito|ImpostaHMin (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniNOffMin) (Variabili|Predefinito|OttieniDmgMin) bOff) Mul) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnScale) 1.0)))
  (Variabili|Predefinito|ImpostaHMax (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniNOffMax) (Variabili|Predefinito|OttieniDmgMax) bOff) Mul) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnScale) 1.0)))
  (Variabili|Predefinito|ImpostaHFlank (Matematica|Float|SelectFloat 0.0 (Variabili|Predefinito|OttieniFlank) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniNRange) 0.0)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|StrikePlayer (Variabili|Predefinito|OttieniMgr) :Attacker (Variabili|Ottieniunriferimentoasestesso) :Atk (Variabili|Predefinito|OttieniHAtk) :DmgMin (Variabili|Predefinito|OttieniHMin) :DmgMax (Variabili|Predefinito|OttieniHMax) :Scale (Variabili|Predefinito|OttieniDmgScale) :Crit (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniCrit) (Variabili|Predefinito|OttieniNOwnCrit)) :Pen (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPen) (Variabili|Predefinito|OttieniNOwnPen)) :Bonus (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniDmgBonus) (Variabili|Predefinito|OttieniNOwnBonus)) :Flank (Variabili|Predefinito|OttieniHFlank)))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniFoe))
        (:then
          (Funzionedichiamata|HitNpcFoe))))))
