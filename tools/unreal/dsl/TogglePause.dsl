(fn TogglePause ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPaused)
    (:then
      (Variabili|Predefinito|ImpostaPaused "false")
      (Gioco|SetGamePaused :bPaused "false")
      (Funzionedichiamata|ShowTalents)
      (Funzionedichiamata|RunQueuedAttack)
      (Funzionedichiamata|RunQueuedTalent))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Variabili|Predefinito|OttieniGameOver))
        (:else
          (Variabili|Predefinito|ImpostaPaused "true")
          (Gioco|SetGamePaused :bPaused "true")
          (Funzionedichiamata|ShowTalents)
          (Funzionedichiamata|ShowMsg :Txt "Paused"))))))
