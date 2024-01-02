<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - B.1 Part)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			18/11/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields, exclude PIX code, patient death section logic fixed

		Version:		1.2
		Date:			29/09/2017
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Bug fixed- Drug name not appearing for B.1.8a  

-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!-- B.1 Patient -->
	<xsl:template match="hl7:primaryRole" mode="patient">
		<!-- B.1.1 Patient characteristics -->
		<xsl:apply-templates select="hl7:player1" mode="patient-characteristics"/>
		<!-- B.1.2 Patient age -->
		<xsl:apply-templates select="hl7:player1" mode="patient-age"/>
		<!-- B.1.3 - B.1.6 Patient other characteristics -->
		<xsl:apply-templates select="." mode="patient-other-characteristics"/>
		<!-- B.1.7 Patient medical history -->
		<xsl:apply-templates select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:observation" mode="patient-medical-history"/>
		<!-- B.1.8. Relevant past drug -->
		<xsl:apply-templates select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugHistory and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:substanceAdministration" mode="patient-drug-history"/>
		<!-- B.1.9. In case of death -->
		<xsl:apply-templates select="." mode="patient-death"/>
		<!-- B.1.10 Parent -->
		<xsl:apply-templates select="hl7:player1/hl7:role[hl7:code/@code=$Parent]" mode="parent"/>
	</xsl:template>
	
	<!-- B.1.1 Patient -->
	<xsl:template match="hl7:player1" mode="patient-characteristics">
		<!-- if Patient Age Group = Foetus: set Foetus as patient name -->
		<patientinitial>
			<xsl:choose>
				<xsl:when test="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$AgeGroup and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code = 0">
					<xsl:text>FOETUS</xsl:text>
				</xsl:when>
				<xsl:when test="hl7:name/@nullFlavor = 'UNK'">UNKNOWN</xsl:when>
				<xsl:when test="hl7:name/@nullFlavor = 'ASKU'">UNKNOWN</xsl:when>
				<xsl:when test="hl7:name/@nullFlavor = 'NASK'">UNKNOWN</xsl:when>
				<xsl:when test="hl7:name/@nullFlavor = 'MSK'">PRIVACY</xsl:when>
				<xsl:otherwise>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string" select="hl7:name"/>
						<xsl:with-param name="string-length">10</xsl:with-param>
					</xsl:call-template>
				</xsl:otherwise>
			</xsl:choose>
		</patientinitial>
		<!-- B.1.1.1 Patient medical records -->
		<patientgpmedicalrecordnumb>
			<xsl:value-of select="hl7:asIdentifiedEntity[hl7:code/@code=$GPMrn]/hl7:id/@extension"/>
		</patientgpmedicalrecordnumb>
		<patientspecialistrecordnumb>
			<xsl:value-of select="hl7:asIdentifiedEntity[hl7:code/@code=$SpecialistMrn]/hl7:id/@extension"/>
		</patientspecialistrecordnumb>
		<patienthospitalrecordnumb>
			<xsl:value-of select="hl7:asIdentifiedEntity[hl7:code/@code=$HospitalMrn]/hl7:id/@extension"/>
		</patienthospitalrecordnumb>
		<patientinvestigationnumb>
			<xsl:value-of select="hl7:asIdentifiedEntity[hl7:code/@code=$Investigation]/hl7:id/@extension"/>
		</patientinvestigationnumb>
	</xsl:template>
	
	<!-- B.1.2. Age information -->
	<xsl:template match="hl7:player1" mode="patient-age">
		<!-- B.1.2.1b Date of birth -->
		<xsl:if test="string-length(hl7:birthTime/@value) > 0">
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">patientbirthdate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:birthTime/@value"/>
				<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		<!-- B.1.2.2a Age at time of onset of reaction / event -->
		<patientonsetage>
			<xsl:value-of select="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$Age and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
		</patientonsetage>
		<patientonsetageunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$Age and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@unit"/>
			</xsl:call-template>
		</patientonsetageunit>
		<!-- B.1.2.2.1 Gestation period when reaction / event was observed in the foetus -->
		<gestationperiod>
			<xsl:value-of select="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$GestationPeriod and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
		</gestationperiod>
		<gestationperiodunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$GestationPeriod and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@unit"/>
			</xsl:call-template>
		</gestationperiodunit>
		<!-- B.1.2.3 Age group ; field not set in case of "Foetus" -->
		<xsl:if test="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$AgeGroup and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code != 0">
			<patientagegroup>
				<xsl:value-of select="../hl7:subjectOf2/hl7:observation[hl7:code/@code=$AgeGroup and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
			</patientagegroup>
		</xsl:if>
	</xsl:template>
	
	<!-- B.1.3. - B.1.6. Patient other characteristics -->
	<xsl:template match="hl7:primaryRole" mode="patient-other-characteristics">
		<!-- B.1.3 Patient weight -->
		<patientweight>
			<xsl:value-of select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$BodyWeight and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
		</patientweight>
		<!-- B.1.4 Patient height -->
		<patientheight>
			<xsl:value-of select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Height and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
		</patientheight>
		<!-- B.1.5 Patient gender - only if not a null flavor -->
		<xsl:if test="hl7:player1/hl7:administrativeGenderCode/@code and hl7:player1/hl7:administrativeGenderCode/@code != 0">
			<patientsex>
				<xsl:value-of select="hl7:player1/hl7:administrativeGenderCode/@code"/>
			</patientsex>
		</xsl:if>
		<!-- B.1.6 Patient last menstruation period date -->
		<xsl:if test="string-length(hl7:subjectOf2/hl7:observation[hl7:code/@code=$LastMenstrualPeriodDate and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value) > 0">
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">patientlastmenstrualdate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$LastMenstrualPeriodDate and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
				<xsl:with-param name="min-format">CCYYMM</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		<!-- B.1.7.2 Text for relevant medical history and concurrent conditions -->
		<patientmedicalhistorytext>
			<xsl:value-of select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:observation[hl7:code/@code=$HistoryAndConcurrentConditionText and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/>
		</patientmedicalhistorytext>
		<!-- B.3.2. Results of tests and procedures relevant to the investigation of the patient -->
		<xsl:variable name="resultsTests">
			<xsl:apply-templates select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$TestsAndProceduresRelevantToTheInvestigation and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:observation" mode="results-tests-procedures"/>
		</xsl:variable>
		<resultstestsprocedures>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string">
					<xsl:value-of select="$resultsTests"/>
				</xsl:with-param>
				<xsl:with-param name="string-length">2000</xsl:with-param>
			</xsl:call-template>
		</resultstestsprocedures>
	</xsl:template>
	
	<!-- B.3.2. Results of tests and procedures relevant to the investigation of the patient -->
	<xsl:template match="hl7:observation" mode="results-tests-procedures">
		<xsl:if test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment and hl7:code/@codeSystem=$oidObservationCode]/hl7:value) > 0 or (string-length(hl7:interpretationCode/@code) > 0 and string-length(hl7:value[@xsi:type='ED']) + count(hl7:value/hl7:center) + count(hl7:value/hl7:low) > 0)">
			<!-- Rule :concatenate all occurrences of B.3.r.b, B.3.r.c1 and B.3.r.f into unique field B.3.2 -->
			<xsl:text>TEST </xsl:text>
			<xsl:if test="string-length(hl7:code/@code) > 0"><xsl:value-of select="hl7:code/@code"/><xsl:text> </xsl:text>(<xsl:value-of select="hl7:code/@codeSystemVersion"/>)<xsl:text> </xsl:text></xsl:if>
			<xsl:if test="string-length(hl7:code/hl7:originalText) > 0"><xsl:value-of select="hl7:code/hl7:originalText"/><xsl:text> </xsl:text></xsl:if>
			<xsl:if test="string-length(hl7:effectiveTime/@value) > 0">(<xsl:value-of select="hl7:effectiveTime/@value"/>)<xsl:text> </xsl:text></xsl:if>
			<xsl:if test="string-length(hl7:interpretationCode/@code) > 0 and string-length(hl7:value[@xsi:type='ED']) + count(hl7:value/hl7:center) + count(hl7:value/hl7:low) > 0">[RESULT : <xsl:call-template name="testresult"/>]<xsl:text> </xsl:text></xsl:if>
			<xsl:if test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment and hl7:code/@codeSystem=$oidObservationCode]/hl7:value) > 0"><xsl:text>: </xsl:text><xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/></xsl:if>
			<xsl:if test="position()!=last()"><xsl:text>; </xsl:text></xsl:if>
		</xsl:if>
	</xsl:template>
	
	<xsl:template name="testresult">
		<xsl:choose>
			<xsl:when test="count(hl7:value/hl7:center) = 1">							<!-- single quantity -->
				<xsl:value-of select="hl7:value/hl7:center/@value"/>
				<xsl:if test="hl7:value/hl7:center/@unit != 1">
					<xsl:text> </xsl:text>
					<xsl:value-of select="hl7:value/hl7:center/@unit"/>
				</xsl:if>
			</xsl:when>
			<xsl:when test="count(hl7:value/hl7:low) = 1"> 								<!-- interval -->
				<xsl:choose>
					<xsl:when test="hl7:value/hl7:low/@nullFlavor='NINF'">			<!-- interval less (or equal) than PQ -->
						<xsl:text>&lt;</xsl:text>
						<xsl:if test="hl7:value/hl7:high/@inclusive=true()"><xsl:text>=</xsl:text></xsl:if>
						<xsl:value-of select="hl7:value/hl7:high/@value"/>
						<xsl:if test="hl7:value/hl7:high/@unit != 1">
							<xsl:text> </xsl:text>
							<xsl:value-of select="hl7:value/hl7:high/@unit"/>
						</xsl:if>
					</xsl:when>
					<xsl:when test="hl7:value/hl7:high/@nullFlavor='PINF'">			<!-- interval greater (or equal) than PQ -->
						<xsl:text>&gt;</xsl:text>
						<xsl:if test="hl7:value/hl7:low/@inclusive=true()"><xsl:text>=</xsl:text></xsl:if>
						<xsl:value-of select="hl7:value/hl7:low/@value"/>					
						<xsl:if test="hl7:value/hl7:low/@unit != 1">
							<xsl:text> </xsl:text>
							<xsl:value-of select="hl7:value/hl7:low/@unit"/>
						</xsl:if>
					</xsl:when>
				</xsl:choose>
			</xsl:when>
			<xsl:when test="hl7:value/@xsi:type = 'ED'">									<!-- unstructured -->
				<xsl:value-of select="hl7:value"/>
			</xsl:when>
		</xsl:choose>
	</xsl:template>
	
	<!-- B.1.7. Relevant medical history and concurrent conditions -->
	<xsl:template match="hl7:observation" mode="patient-medical-history">
		<!-- B.1.7.2 is treated elsewhere and B.1.7.3 is ignored -->
		<xsl:if test="(hl7:code/@code != $HistoryAndConcurrentConditionText and hl7:code/@code != $ConcommitantTherapy) or string-length(hl7:code/@code) = 0">
			<medicalhistoryepisode>
				<patientepisodenamemeddraversion>
					<xsl:value-of select="hl7:code/@codeSystemVersion"/>
				</patientepisodenamemeddraversion>
				<patientepisodename>
					<xsl:value-of select="hl7:code/@code"/>
					<xsl:if test="string-length(hl7:code/@code) = 0"><xsl:value-of select="hl7:code/hl7:originalText"/></xsl:if>
				</patientepisodename>
				<xsl:if test="string-length(hl7:effectiveTime/hl7:low/@value) > 0">
					<xsl:call-template name="convertDate">
						<xsl:with-param name="elementName">patientmedicalstartdate</xsl:with-param>
						<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
						<xsl:with-param name="min-format">CCYY</xsl:with-param>
						<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
					</xsl:call-template>
				</xsl:if>
				<xsl:if test="string-length(hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value) + string-length(hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor)> 0" >
					<patientmedicalcontinue>
						<xsl:call-template name="getMapping">
							<xsl:with-param name="type">YESNO</xsl:with-param>
							<xsl:with-param name="code" select="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
						</xsl:call-template>
						<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'UNK'">3</xsl:if>
						<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'ASKU'">3</xsl:if>
						<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'NASK'">3</xsl:if>
					</patientmedicalcontinue>
				</xsl:if>
				<xsl:if test="string-length(hl7:effectiveTime/hl7:high/@value)>0" >
					<xsl:call-template name="convertDate">
						<xsl:with-param name="elementName">patientmedicalenddate</xsl:with-param>
						<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:high/@value"/>
						<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
					</xsl:call-template>
				</xsl:if>
				<patientmedicalcomment>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string" select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/>
						<xsl:with-param name="string-length">100</xsl:with-param>
					</xsl:call-template>
				</patientmedicalcomment>
			</medicalhistoryepisode>
		</xsl:if>
	</xsl:template>
	
	<!-- B.1.8. Relevant past drug -->
	<xsl:template match="hl7:substanceAdministration" mode="patient-drug-history">
		<patientpastdrugtherapy>
			<!-- B.1.8.r.a0 PatientDrugname - prefixed with MPID and PhPID -->
			<patientdrugname>
			<!-- D.8.r.EU.r.1 Patient Drug name substance information-->
				<xsl:variable name="patientDrugName">
					<xsl:call-template name="DrugName" />
				</xsl:variable>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="$patientDrugName"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">100</xsl:with-param>
				</xsl:call-template>
			</patientdrugname>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:low/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">patientdrugstartdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:high/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">patientdrugenddate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:high/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<patientindicationmeddraversion>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Indication and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@codeSystemVersion"/>
			</patientindicationmeddraversion>
			<patientdrugindication>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Indication and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
			</patientdrugindication>
			<patientdrgreactionmeddraversion>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Reaction and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@codeSystemVersion"/>
			</patientdrgreactionmeddraversion>
			<patientdrugreaction>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Reaction and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
			</patientdrugreaction>
		</patientpastdrugtherapy>
	</xsl:template>
	
	<!-- B.1.(10.)8.r.a0 Drugname - prefixed with MPID and PhPID  exclude PIX code-->
	<!-- EU Substance name D.10.8.r.EU.r.1 & D.8.r.EU.r.1 -->
	<xsl:template name="DrugName">
		<!-- <xsl:if test="string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@code) > 0 or string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient/hl7:ingredientSubstance/hl7:name) >0"> -->
			<xsl:if test="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@codeSystem = $MPID">
				<xsl:text>MPID: </xsl:text>
				<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@code"/>
				<xsl:text> (</xsl:text>
				<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@codeSystemVersion"/>
				<xsl:text>)</xsl:text>
			</xsl:if>
			<xsl:if test="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@codeSystem = $PhPID">
				<xsl:text>PhPID: </xsl:text>
				<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@code"/>
				<xsl:text> (</xsl:text>
				<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:code/@codeSystemVersion"/>
				<xsl:text>)</xsl:text>
			</xsl:if>
			<xsl:if test="string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient/hl7:ingredientSubstance/hl7:name) >0">
					<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient/hl7:ingredientSubstance/hl7:name"/>
					<xsl:text>: </xsl:text>
			</xsl:if>
			<xsl:if test="string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:name) > 0">
					<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:name"/>
			</xsl:if>
			
		<!-- </xsl:if> -->
		
	</xsl:template>
	
	<!-- B.1.9. In case of death -->
	<xsl:template match="hl7:primaryRole" mode="patient-death">
		<xsl:if test="string-length(hl7:player1/hl7:deceasedTime/@value) > 0 or string-length(hl7:player1/hl7:deceasedTime/@nullFlavor) > 0 or string-length(hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value) > 0 or string-length(hl7:subjectOf2/hl7:observation[hl7:code/@code=$ReportedCauseOfDeath and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code) > 0 or string-length(hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CauseOfDeath and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code) > 0">
			<patientdeath>
				<xsl:if test="string-length(hl7:player1/hl7:deceasedTime/@value) > 0">
					<xsl:call-template name="convertDate">
						<xsl:with-param name="elementName">patientdeathdate</xsl:with-param>
						<xsl:with-param name="date-value" select="hl7:player1/hl7:deceasedTime/@value"/>
						<xsl:with-param name="min-format">CCYY</xsl:with-param>
						<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
					</xsl:call-template>
				</xsl:if>
				<patientautopsyyesno>
					<xsl:call-template name="getMapping">
						<xsl:with-param name="type">YESNO</xsl:with-param>
						<xsl:with-param name="code" select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
					</xsl:call-template>
					<xsl:if test="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'UNK'">3</xsl:if>
					<xsl:if test="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'ASKU'">3</xsl:if>
					<xsl:if test="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'NASK'">3</xsl:if>
				</patientautopsyyesno>
				<xsl:apply-templates select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$ReportedCauseOfDeath and hl7:code/@codeSystem=$oidObservationCode]" mode="patient-death-cause"/>
				<xsl:apply-templates select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Autopsy and hl7:code/@codeSystem=$oidObservationCode]/hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CauseOfDeath and hl7:code/@codeSystem=$oidObservationCode]" mode="patient-autopsy"/>
			</patientdeath>
		</xsl:if>
	</xsl:template>
	
	<!-- B.1.9.2. Patient reported cause of death -->
	<xsl:template match="hl7:observation" mode="patient-death-cause">
		<patientdeathcause>
			<patientdeathreportmeddraversion>
				<xsl:value-of select="hl7:value/@codeSystemVersion"/>
			</patientdeathreportmeddraversion>
			<patientdeathreport>
				<xsl:choose>
					<xsl:when test="string-length(hl7:value/@code) > 0"><xsl:value-of select="hl7:value/@code"/></xsl:when>
					<xsl:otherwise><xsl:value-of select="hl7:value/hl7:originalText"/></xsl:otherwise>
				</xsl:choose>
			</patientdeathreport>
		</patientdeathcause>
	</xsl:template>
	
	<!-- B.1.9.4. Patient autopsy-determined cause of death -->
	<xsl:template match="hl7:observation" mode="patient-autopsy">
		<patientautopsy>
			<patientdetermautopsmeddraversion>
				<xsl:value-of select="hl7:value/@codeSystemVersion"/>
			</patientdetermautopsmeddraversion>
			<patientdetermineautopsy>
				<xsl:choose>
					<xsl:when test="string-length(hl7:value/@code) > 0"><xsl:value-of select="hl7:value/@code"/></xsl:when>
					<xsl:otherwise><xsl:value-of select="hl7:value/hl7:originalText"/></xsl:otherwise>
				</xsl:choose>
			</patientdetermineautopsy>
		</patientautopsy>
	</xsl:template>
	
	<!-- B.1.10. Parent - For a parent-child/foetus report, information concerning the parent -->
	<xsl:template match="hl7:role" mode="parent">
		<parent>
			<parentidentification>
				<xsl:choose>
					<xsl:when test="hl7:associatedPerson/hl7:name/@nullFlavor = 'UNK'">UNKNOWN</xsl:when>
					<xsl:when test="hl7:associatedPerson/hl7:name/@nullFlavor = 'MSK'">PRIVACY</xsl:when>
					<xsl:otherwise>
						<xsl:call-template name="truncate">
							<xsl:with-param name="string" select="hl7:associatedPerson/hl7:name"/>
							<xsl:with-param name="string-length">10</xsl:with-param>
						</xsl:call-template>
					</xsl:otherwise>
				</xsl:choose>
			</parentidentification>
			<xsl:if test="string-length(hl7:associatedPerson/hl7:birthTime/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentbirthdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:associatedPerson/hl7:birthTime/@value"/>
					<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<!-- B.1.10.2.2 Parent age -->
			<parentage>
				<xsl:value-of select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Age and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
			</parentage>
			<parentageunit><xsl:value-of select="$Year"/></parentageunit>
			<xsl:if test="string-length(hl7:subjectOf2/hl7:observation[hl7:code/@code=$LastMenstrualPeriodDate and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentlastmenstrualdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$LastMenstrualPeriodDate and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
					<xsl:with-param name="min-format">CCYYMMDD</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<parentweight>
				<xsl:value-of select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$BodyWeight and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
			</parentweight>
			<parentheight>
				<xsl:value-of select="hl7:subjectOf2/hl7:observation[hl7:code/@code=$Height and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
			</parentheight>
			<xsl:if test="hl7:associatedPerson/hl7:administrativeGenderCode/@code and hl7:associatedPerson/hl7:administrativeGenderCode/@code != 0">
				<parentsex>
					<xsl:value-of select="hl7:associatedPerson/hl7:administrativeGenderCode/@code"/>
				</parentsex>
			</xsl:if>
			<parentmedicalrelevanttext>
				<xsl:value-of select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:observation[hl7:code/@code=$HistoryAndConcurrentConditionText and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/>
			</parentmedicalrelevanttext>
			<!-- B.1.10.7 Parent medical history -->
			<xsl:apply-templates select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:observation[hl7:code/@code != $HistoryAndConcurrentConditionText or string-length(hl7:code/@code) = 0]" mode="parent-medical-history"/>
			<!-- B.1.10.8 Parent drug history -->
			<xsl:apply-templates select="hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugHistory and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:substanceAdministration" mode="parent-drug-history"/>
		</parent>
	</xsl:template>
	
	<!-- B.1.10.7. Relevant medical history and concurrent conditions of parent -->
	<xsl:template match="hl7:observation" mode="parent-medical-history">
		<parentmedicalhistoryepisode>
			<parentmdepisodemeddraversion>
				<xsl:value-of select="hl7:code/@codeSystemVersion"/>
			</parentmdepisodemeddraversion>
			<parentmedicalepisodename>
				<xsl:value-of select="hl7:code/@code"/>
				<xsl:if test="string-length(hl7:code/@code) = 0"><xsl:value-of select="hl7:code/hl7:originalText"/></xsl:if>
			</parentmedicalepisodename>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:low/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentmedicalstartdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<parentmedicalcontinue>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type">YESNO</xsl:with-param>
					<xsl:with-param name="code" select="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value"/>
				</xsl:call-template>
				<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'UNK'">3</xsl:if>
				<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'ASKU'">3</xsl:if>
				<xsl:if test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Continuing and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@nullFlavor = 'NASK'">3</xsl:if>
			</parentmedicalcontinue>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:high/@value)>0" >
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentmedicalenddate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:high/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<parentmedicalcomment>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">100</xsl:with-param>
				</xsl:call-template>
			</parentmedicalcomment>
		</parentmedicalhistoryepisode>
	</xsl:template>
	
	<!-- B.1.10.8. Relevant past drug history -->
	<xsl:template match="hl7:substanceAdministration" mode="parent-drug-history">
		<parentpastdrugtherapy>
			<!-- B.1.10.8.r.a0 PatientDrugname - prefix MPID and PhPID -->
			<parentdrugname>
				<xsl:variable name="parentDrugName">
					<xsl:call-template name="DrugName" />
				</xsl:variable>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="$parentDrugName"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">100</xsl:with-param>
				</xsl:call-template>
			</parentdrugname>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:low/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentdrugstartdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<xsl:if test="string-length(hl7:effectiveTime/hl7:high/@value) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">parentdrugenddate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:high/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<parentdrgindicationmeddraversion>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Indication and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@codeSystemVersion"/>
			</parentdrgindicationmeddraversion>
			<parentdrugindication>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Indication and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
			</parentdrugindication>
			<parentdrgreactionmeddraversion>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Reaction and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@codeSystemVersion"/>
			</parentdrgreactionmeddraversion>
			<parentdrugreaction>
				<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Reaction and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
			</parentdrugreaction>
		</parentpastdrugtherapy>
	</xsl:template>
	
</xsl:stylesheet>
