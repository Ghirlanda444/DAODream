(fn LootMake ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniWLoot))
    (:else
      (bind _w (InterfacciaUtente|Creawidget "/Game/Cousland/Combat/WBP_Loot.WBP_Loot_C" (Gioco|GetPlayerController 0)))
      (bind _t (Utilità|Casting|CastToWBP_Loot _w))
      (Variabili|Predefinito|ImpostaWLoot _t))))
