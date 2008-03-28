import FWCore.ParameterSet.Config as cms

# module to produce jet correction factors associated in a valuemap
jetCorrFactors = cms.EDProducer("JetCorrFactorsProducer",
    gluonJetCorrector = cms.string('L5FlavorJetCorrectorGluon'),
    jetSource = cms.InputTag("iterativeCone5CaloJets"),
    cJetCorrector = cms.string('L5FlavorJetCorrectorC'),
    bJetCorrector = cms.string('L5FlavorJetCorrectorB'),
    udsJetCorrector = cms.string('L5FlavorJetCorrectorUds'),
    defaultJetCorrector = cms.string('MCJetCorrectorIcone5')
)


