(fn GenReact2 ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Minore(<) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniGHc)) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniLRules) 0)) (Utility|Operatori|Minore(<) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniGMn)) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniLRules) 0)))
    (:then
      (Variabili|Predefinito|ImpostaGLim (Matematica|Float|Max(Float) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniLRules) 0) 1.0))
      (Variabili|Predefinito|ImpostaGChance (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Utility|Operatori|Dividi (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utility|Operatori|Dividi (Matematica|Conversioni|ToFloat(Integer) (Matematica|Intero|Min(Integer) (Variabili|Predefinito|OttieniGHc) (Variabili|Predefinito|OttieniGMn))) (Variabili|Predefinito|OttieniGLim)) -1.0) 1.0) 4.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniLRules) 1)) (Matematica|Float|Max(Float) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 2) 1.0)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Matematica|Casuale|RandomFloat) (Variabili|Predefinito|OttieniGChance))
    (:then
      (Funzionedichiamata|GenReact3))))))
