(fn GenLoot (InLoot O BStart BCount bHost)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniGItems))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniGCounts))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniGEquip))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniGLoot))
  (Variabili|Predefinito|ImpostaGMoney 0)
  (Variabili|Predefinito|ImpostaGCarry "false")
  (Variabili|Predefinito|ImpostaGHost bHost)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 8
    (:LoopBody
      (Funzionedichiamata|GCopy :InLoot InLoot :O O :J _index))
    (:Completed
      (Funzionedichiamata|GenBag :BStart BStart :BCount BCount)
      (Funzionedichiamata|GenReactive)
      (Funzionedichiamata|GenFirst)
      (Funzionedichiamata|GenDraws)
      (Funzionedichiamata|GenEquip))))
