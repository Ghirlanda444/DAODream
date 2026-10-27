(fn OpenBox (Box)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPContainer|OttieniUsable Box)
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPContainer|OttieniLocked Box)
    (:then
      (Funzionedichiamata|TryUnlock :Box Box))
    (:else
      (Funzionedichiamata|ShowLoot :Box Box))))))
