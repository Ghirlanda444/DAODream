(fn BidKeep (Follower)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Classe|BPDlgNPC|OttieniTarget Follower)) (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead (Classe|BPDlgNPC|OttieniTarget Follower))))
    (:else
      (Classe|BPDlgNPC|SetTarget Follower))))
