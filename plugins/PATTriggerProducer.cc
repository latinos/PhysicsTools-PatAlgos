//
// $Id: PATTriggerProducer.cc,v 1.1.2.7 2009/03/13 12:10:36 vadler Exp $
//


#include "PhysicsTools/PatAlgos/plugins/PATTriggerProducer.h"


using namespace pat;

PATTriggerProducer::PATTriggerProducer( const edm::ParameterSet & iConfig ) :
  nameProcess_( iConfig.getParameter< std::string >( "processName" ) ),
  tagTriggerResults_( iConfig.getParameter< edm::InputTag >( "triggerResults" ) ),
  tagTriggerEvent_( iConfig.getParameter< edm::InputTag >( "triggerEvent" ) ),
  addPathModuleLabels_( iConfig.getParameter< bool >( "addPathModuleLabels" ) )
{
  if ( tagTriggerResults_.process().empty() ) {
    tagTriggerResults_ = edm::InputTag( tagTriggerResults_.label(), tagTriggerResults_.instance(), nameProcess_ );
  }
  if ( tagTriggerEvent_.process().empty() ) {
    tagTriggerEvent_ = edm::InputTag( tagTriggerEvent_.label(), tagTriggerEvent_.instance(), nameProcess_ );
  }

  produces< TriggerPathCollection >();
  produces< TriggerFilterCollection >();
  produces< TriggerObjectCollection >();
}

PATTriggerProducer::~PATTriggerProducer()
{
}

void PATTriggerProducer::beginRun( edm::Run & iRun, const edm::EventSetup & iSetup )
{
  if ( ! hltConfig_.init( nameProcess_ ) ) {
    edm::LogError( "errorHltConfigExtraction" ) << "HLT config extraction error with process name " << nameProcess_;
    return;
  }                          
}

void PATTriggerProducer::produce( edm::Event& iEvent, const edm::EventSetup& iSetup )
{
  if ( hltConfig_.size() <= 0 ) {
    edm::LogError( "errorHltConfigSize" ) << "HLT config size error" << "\n"
                                          << "Check for occurence of an \"errorHltConfigExtraction\" from beginRun()";
    return;
  }
  edm::Handle< edm::TriggerResults > handleTriggerResults;
  iEvent.getByLabel( tagTriggerResults_, handleTriggerResults );
  if ( ! handleTriggerResults.isValid() ) {
    edm::LogError( "errorTriggerResultsValid" ) << "edm::TriggerResults product with InputTag " << tagTriggerResults_.encode() << " not in event";
    return;
  }
  edm::Handle< trigger::TriggerEvent > handleTriggerEvent;
  iEvent.getByLabel( tagTriggerEvent_, handleTriggerEvent );
  if ( ! handleTriggerEvent.isValid() ) {
    edm::LogError( "errorTriggerEventValid" ) << "trigger::TriggerEvent product with InputTag " << tagTriggerEvent_.encode() << " not in event";
    return;
  }

  // produce trigger paths and determine status of modules
  
  const unsigned sizePaths( hltConfig_.size() );
  const unsigned sizeFilters( handleTriggerEvent->sizeFilters() );
    
  std::auto_ptr< TriggerPathCollection > triggerPaths( new TriggerPathCollection() );
  triggerPaths->reserve( sizePaths );
  
  std::map< std::string, int >              moduleStates;
  std::multimap< std::string, std::string > filterPaths;
  
  for ( unsigned iP = 0; iP < sizePaths; ++iP ) {
    // initialize path
    const std::string namePath( hltConfig_.triggerName( iP ) );
    const unsigned indexPath( hltConfig_.triggerIndex( namePath ) );
    const unsigned indexLastFilter( handleTriggerResults->index( indexPath ) );
    TriggerPath triggerPath( namePath, indexPath, 0, handleTriggerResults->wasrun( indexPath ), handleTriggerResults->accept( indexPath ), handleTriggerResults->error( indexPath ), indexLastFilter );
    // add module names to path and states' map
    const unsigned sizeModules( hltConfig_.size( namePath ) );
    assert( indexLastFilter < sizeModules );
    std::map< unsigned, std::string > indicesModules;
    for ( unsigned iM = 0; iM < sizeModules; ++iM ) {
      const std::string nameModule( hltConfig_.moduleLabel( indexPath, iM ) );
      if ( addPathModuleLabels_ ) {
        triggerPath.addModule( nameModule );
      }
      const unsigned indexFilter( handleTriggerEvent->filterIndex( edm::InputTag( nameModule, "", nameProcess_ ) ) );
      if ( indexFilter < sizeFilters ) {
        triggerPath.addFilterIndex( indexFilter );
        filterPaths.insert( std::pair< std::string, std::string >( nameModule, namePath ) );
      }
      const unsigned slotModule( hltConfig_.moduleIndex( indexPath, nameModule ) ); 
      indicesModules.insert( std::pair< unsigned, std::string >( slotModule, nameModule ) );
    }
    // store path
    triggerPaths->push_back( triggerPath );
    // store module states to be used for the filters
    for ( std::map< unsigned, std::string >::const_iterator iM = indicesModules.begin(); iM != indicesModules.end(); ++iM ) {
      if ( iM->first < indexLastFilter ) {
        moduleStates[ iM->second ] = 1;
      } else if ( iM->first == indexLastFilter ) {
        moduleStates[ iM->second ] = handleTriggerResults->accept( indexPath );
      } else if ( moduleStates.find( iM->second ) == moduleStates.end() ) {
        moduleStates[ iM->second ] = -1;
      }
    }
  }
  
  iEvent.put( triggerPaths );
  
  // produce trigger filters and store used trigger object types
  // (only last active filter(s) available from trigger::TriggerEvent)
  
  std::auto_ptr< TriggerFilterCollection > triggerFilters( new TriggerFilterCollection() );
  triggerFilters->reserve( sizeFilters );
  
  std::multimap< trigger::size_type, int >         filterIds;
  std::multimap< trigger::size_type, std::string > filterLabels;
  
  for ( unsigned iF = 0; iF < sizeFilters; ++iF ) {
    const std::string nameFilter( handleTriggerEvent->filterTag( iF ).label() );
    TriggerFilter triggerFilter( nameFilter );
    // set filter type
    const std::string typeFilter( hltConfig_.moduleType( nameFilter ) );
    triggerFilter.setType( typeFilter );
    // set filter IDs of used objects
    const trigger::Keys & keys = handleTriggerEvent->filterKeys( iF );
    const trigger::Vids & ids  = handleTriggerEvent->filterIds( iF );   
    for ( unsigned iK = 0; iK < keys.size(); ++iK ) {
      triggerFilter.addObjectKey( keys[ iK ] );
      filterLabels.insert( std::pair< trigger::size_type, std::string >( keys[ iK ], nameFilter ) ); // only for objects used in last active filter
    }
    for ( unsigned iI = 0; iI < ids.size(); ++iI ) {
      triggerFilter.addObjectId( ids[ iI ] );
    }
    // set status from path info
    std::map< std::string, int >::iterator iS( moduleStates.find( nameFilter ) );
    if ( iS != moduleStates.end() ) {
      if ( ! triggerFilter.setStatus( iS->second ) ) {
        triggerFilter.setStatus( -1 ); // different code for "unvalid status determined" needed?
      }
    } else {
      triggerFilter.setStatus( -1 ); // different code for "unknown" needed?
    }
    // store filter
    triggerFilters->push_back( triggerFilter );
    // store used trigger object types to be used with the objects
    assert( ids.size() == keys.size() );
    for ( unsigned iK = 0; iK < keys.size(); ++iK ) {
      filterIds.insert( std::pair< trigger::size_type, int >( keys[ iK ], ids[ iK ] ) );             // only for objects used in last active filter
    }
  }

  iEvent.put( triggerFilters );
  
  // produce trigger objects
  
  const unsigned sizeObjects( handleTriggerEvent->sizeObjects() );
  
  std::auto_ptr< TriggerObjectCollection > triggerObjects( new TriggerObjectCollection() );
  triggerObjects->reserve( sizeObjects );
  
  const trigger::Keys & collectionKeys( handleTriggerEvent->collectionKeys() );
  for ( unsigned iO = 0, iC = 0; iO < sizeObjects && iC < handleTriggerEvent->sizeCollections(); ++iO ) {
    TriggerObject triggerObject( handleTriggerEvent->getObjects().at( iO ) );
    // set collection
    while ( iO >= collectionKeys[ iC ] ) {
      ++iC;
    } // relies on well ordering of trigger objects with respect to the collections
    triggerObject.setCollection( handleTriggerEvent->collectionTag( iC ).encode() );
    // set filter ID
    for ( std::multimap< trigger::size_type, int >::iterator iM = filterIds.begin(); iM != filterIds.end(); ++iM ) {
      if ( iM->first == iO && ! triggerObject.hasFilterId( iM->second ) ) {
        triggerObject.addFilterId( iM->second );
      }
    }
    // add transient filter label and path name
    for ( std::multimap< trigger::size_type, std::string >::iterator iM = filterLabels.begin(); iM != filterLabels.end(); ++iM ) {
      if ( iM->first == iO ) {
        for ( std::multimap< std::string, std::string >::iterator iP = filterPaths.begin(); iP != filterPaths.end(); ++iP ) {
          if ( iP->first == iM->second ) {
            triggerObject.addPathName( iP->second );
            break;
          }
        }
        triggerObject.addFilterLabel( iM->second );
        break;
      }
    }
    
    triggerObjects->push_back( triggerObject );
  }
  
  iEvent.put( triggerObjects );
}


#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE( PATTriggerProducer );