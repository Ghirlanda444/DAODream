(fn TalentEffect6 (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 14001.0)
    (:then
      (Funzionedichiamata|ShootFx)
      (Funzionedichiamata|SpellHitFoe :Amount (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniSpellPower) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 14000.0)
        (:then
          (Funzionedichiamata|EffShock :K K))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 12006.0)
            (:then
              (Funzionedichiamata|EffMindBlast :K K))
            (:else
              (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 6)) :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)) :bOff "false" :bSure "false"))))))))
