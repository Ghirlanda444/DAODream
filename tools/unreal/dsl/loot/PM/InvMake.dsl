(fn InvMake ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniWInv))
    (:else
      (bind _w (InterfacciaUtente|Creawidget "/Game/Cousland/Combat/WBP_Inventory.WBP_Inventory_C" (Gioco|GetPlayerController 0)))
      (bind _t (Utilità|Casting|CastToWBP_Inventory _w))
      (Variabili|Predefinito|ImpostaWInv _t))))
