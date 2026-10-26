(fn UseRoute ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickNpc))
    (:then
      (Classe|BPDlgNPC|Interact (Variabili|Predefinito|OttieniPickNpc)))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickDoor))
        (:then
          (Classe|BPDoor|TryUse (Variabili|Predefinito|OttieniPickDoor)))))))
