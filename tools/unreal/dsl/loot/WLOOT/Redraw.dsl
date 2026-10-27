(fn Redraw ()
  (Widget|SetText(Text) (Variabili|WBP_Loot|OttieniTitle) (Utilità|Testo|ToText(String) (Classe|BPContainer|OttieniCName (Variabili|Predefinito|OttieniBox))))
  (Classe|BPPlotManager|MoneyText (Variabili|Predefinito|OttieniMgr) :Bits (Classe|BPContainer|OttieniLMoney (Variabili|Predefinito|OttieniBox)))
  (Widget|SetText(Text) (Variabili|WBP_Loot|OttieniMoneyT) (Utilità|Testo|ToText(String) (Utilità|Stringa|SelectString (Utilità|Stringa|Append "Money: " (Classe|BPPlotManager|OttieniMText (Variabili|Predefinito|OttieniMgr))) "No money" (Utility|Operatori|Maggiore(>) (Classe|BPContainer|OttieniLMoney (Variabili|Predefinito|OttieniBox)) 0))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 11
    (:LoopBody
      (Funzionedichiamata|DrawIt :K _index))))
