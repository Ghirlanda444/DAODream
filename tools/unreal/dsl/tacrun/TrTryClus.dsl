(fn TrTryClus (K)
  (Variabili|Predefinito|ImpostaPkN 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)) 1)
    (:LoopBody
      (Funzionedichiamata|TrClusOne :K K :J _index))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniPkN)) (Variabili|Predefinito|OttieniTP)) (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggiore(>) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniPkN)) (Variabili|Predefinito|OttieniPkBest)) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniPkN)) (Variabili|Predefinito|OttieniPkBest)) (Utility|Operatori|Minore(<) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnAll) K)) (Variabili|Predefinito|OttieniPkBestD)))))
    (:then
      (Variabili|Predefinito|ImpostaPkBest (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniPkN)))
      (Variabili|Predefinito|ImpostaPkBestD (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnAll) K)))
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnAll) K)))))))
