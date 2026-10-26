(fn TalentEffect5 (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90047.0)
    (:then
      (Funzionedichiamata|EffShred :K K))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90048.0)
        (:then
          (Funzionedichiamata|EffHowl :K K))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90015.0)
            (:then
              (Funzionedichiamata|EffOverwhelm :K K))
            (:else
              (Funzionedichiamata|TalentEffect6 :K K))))))))
