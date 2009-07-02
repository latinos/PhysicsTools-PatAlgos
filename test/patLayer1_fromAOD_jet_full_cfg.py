import FWCore.ParameterSet.Config as cms

process = cms.Process("PAT")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

# source
process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_3_1_0_pre10/RelValTTbar/GEN-SIM-RECO/IDEAL_31X_v1/0008/CC80B73A-CA57-DE11-BC2F-000423D99896.root'
    )
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('IDEAL_31X::All')
process.load("Configuration.StandardSequences.MagneticField_cff")

# extraction of jet sequences
process.load("PhysicsTools.PatAlgos.recoLayer0.bTagging_cff")         ## empty
process.load("PhysicsTools.PatAlgos.recoLayer0.jetTracksCharge_cff")
process.load("PhysicsTools.PatAlgos.recoLayer0.jetMETCorrections_cff")
process.load("PhysicsTools.PatAlgos.mcMatchLayer0.mcMatchSequences_cff")
process.load("PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi")
process.content = cms.EDAnalyzer("EventContentAnalyzer")

process.p = cms.Path(
     process.patJetCharge *  
     process.patJetCorrections *
     process.jetPartonMatch *
     process.jetGenJetMatch *
     process.jetFlavourId *  
     process.allLayer1Jets # * 
  #  process.content
)

# Output module configuration
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('PATLayer1_Output.fromAOD_full.root'),
    # save only events passing the full path
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    # save PAT Layer 1 output
    outputCommands = cms.untracked.vstring('drop *', *patEventContent ) # you need a '*' to unpack the list of commands 'patEventContent'
)
process.outpath = cms.EndPath(process.out)
