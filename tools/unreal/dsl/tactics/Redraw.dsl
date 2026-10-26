(fn Redraw ()
  (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniTitle) (Utilità|Testo|ToText(String) (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "Tactics: " (Variabili|Predefinito|OttieniMName)) (Utilità|Stringa|Append "   (" (Utilità|Stringa|ToString(Integer) (Variabili|Predefinito|OttieniSlots)))) " slots)")))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 11
    (:LoopBody
      (Funzionedichiamata|DrawRow :R _index))))
