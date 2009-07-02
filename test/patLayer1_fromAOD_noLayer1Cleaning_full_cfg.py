import FWCore.ParameterSet.Config as cms

process = cms.Process("PAT")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

# source
process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring('/store/relval/CMSSW_3_1_0_pre10/RelValTTbar/GEN-SIM-RECO/IDEAL_31X_v1/0008/CC80B73A-CA57-DE11-BC2F-000423D99896.root')
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('IDEAL_31X::All')
process.load("Configuration.StandardSequences.MagneticField_cff")

# PAT Layer 0+1
process.load("PhysicsTools.PatAlgos.patSequences_cff")
#process.content = cms.EDAnalyzer("EventContentAnalyzer")
# replacements currently needed to make the jets work
process.allLayer1Jets.addDiscriminators    = False
process.allLayer1Jets.discriminatorSources = []

from PhysicsTools.PatAlgos.tools.coreTools import removeCleaning
removeCleaning(process)

process.p = cms.Path(
    process.patDefaultSequence  
)

# Output module configuration
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoLayer1Cleaning
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('PATLayer1_Output.fromAOD_noLayer1Cleaning_full.root'),
    # save only events passing the full path
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    # save PAT Layer 1 output
    outputCommands = cms.untracked.vstring('drop *', *patEventContentNoLayer1Cleaning ) # you need a '*' to unpack the list of commands
)
process.outpath = cms.EndPath(process.out)
