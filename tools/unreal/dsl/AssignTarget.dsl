(fn AssignTarget (Follower)
  (bind _o (Classe|BPDlgNPC|OttieniOrderTarget Follower))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _o)
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniDead _o)
        (:then
          (Funzionedichiamata|AssignByBid :Follower Follower))
        (:else
          (Classe|BPDlgNPC|SetTarget Follower :InTarget _o))))
    (:else
      (Funzionedichiamata|AssignByBid :Follower Follower))))
