(fn Redraw ()
  (Classe|BPPlotManager|MoneyText (Variabili|Predefinito|OttieniMgr) :Bits (Classe|BPPlotManager|OttieniMoney (Variabili|Predefinito|OttieniMgr)))
  (Widget|SetText(Text) (Variabili|WBP_Inventory|OttieniMoneyT) (Utilità|Testo|ToText(String) (Classe|BPPlotManager|OttieniMText (Variabili|Predefinito|OttieniMgr))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 19
    (:LoopBody
      (Funzionedichiamata|DrawRow :K _index))))
