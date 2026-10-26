(fn HeroTacticFire (bMode)
  (Utilità|ControlloDiFlusso|Ramo bMode
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniHTFound)) 100000000.0)
        (:else
          (Funzionedichiamata|UseTalentNow :Slot (Variabili|Predefinito|OttieniHTFound))
          (Variabili|Predefinito|ImpostaHTDone (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniHTFound)) 100000000.0)))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTReady) (Variabili|Predefinito|OttieniHTFound)) (Utilità|Testo|GetGameTimeinSeconds))
        (:else
          (Funzionedichiamata|UseTalentNow :Slot (Variabili|Predefinito|OttieniHTFound))
          (Variabili|Predefinito|ImpostaHTDone (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTReady) (Variabili|Predefinito|OttieniHTFound)) (Utilità|Testo|GetGameTimeinSeconds))))))))
