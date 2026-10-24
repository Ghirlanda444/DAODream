(fn StageTick ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniCutPlaying) (Utility|Operatori|Minore(<) (Utility|Operatori|Sottrai (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniStageStart)) (Variabili|Predefinito|OttieniStageLen)))
    (:then (Funzionedichiamata|StageAll))
    (:else (Utilità|Testo|ClearTimerbyFunctionName (Variabili|Ottieniunriferimentoasestesso) "StageTick"))))
