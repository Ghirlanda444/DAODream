(fn TrMeInfoNpc (N)
  (Variabili|Predefinito|ImpostaTMeBeh (Classe|BPDlgNPC|OttieniBehavior N))
  (Variabili|Predefinito|ImpostaTMeHated (Classe|BPDlgNPC|OttieniFoe N))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Classe|BPDlgNPC|OttieniHated N))
    (:then
      (Variabili|Predefinito|ImpostaTMeHated (Classe|BPDlgNPC|OttieniHated N)))))
