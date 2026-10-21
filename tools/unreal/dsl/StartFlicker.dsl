(fn StartFlicker ()
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniFlickerLights))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniFlickerBase))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniFlickerPhase))
  (bind _lights (Attore|GetComponentsByClass :ComponentClass "/Script/Engine.PointLightComponent"))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _lights) 1)
    (:LoopBody
      (bind _c (Utilità|Casting|CastToPointLightComponent (Utilità|Array|Ottieni(unacopia) _lights _index)))
      (Utilità|ControlloDiFlusso|Ramo (Classe|LightComponentBase|OttieniCastShadows _c)
        (:then
          (Utilità|Array|Add (Variabili|Predefinito|OttieniFlickerLights) _c)
          (Utilità|Array|Add (Variabili|Predefinito|OttieniFlickerBase) (Classe|LightComponentBase|OttieniIntensity _c))
          (Utilità|Array|Add (Variabili|Predefinito|OttieniFlickerPhase) (Matematica|Casuale|RandomFloatinRange 0.0 100.0)))))
    (:Completed
      (Utilità|Testo|SetTimerbyFunctionName :Object (Variabili|Ottieniunriferimentoasestesso) :FunctionName "Flicker" :Time 0.05 :bLooping "true"))))
