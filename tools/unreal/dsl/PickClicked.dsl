(fn PickClicked (What)
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC What))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _npc)
    (:then
      (Variabili|Predefinito|ImpostaPickNpc _npc))))
