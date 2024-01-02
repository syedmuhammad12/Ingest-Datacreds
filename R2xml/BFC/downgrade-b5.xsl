<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - B.5 Part)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			07/10/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!--	B.5. Narrative case summary and further information	-->
	<xsl:template match="hl7:investigationEvent" mode="summary">
		<summary>
			<narrativeincludeclinical>
				<!-- B.5.1 Case narrative -->
				<xsl:value-of select="hl7:text"/>
				<!-- Other information coming from the downgrade rules -->
				<xsl:call-template name="CaseSummary" />
				<xsl:call-template name="SummaryAdditionalDocuments" />
				<xsl:call-template name="SummaryDuplicateReports" />
				<xsl:call-template name="SummaryReportNullification" />
				<xsl:call-template name="SummaryReportNullificationReason" />
				<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf1/hl7:researchStudy" mode="SummaryStudyIdentification" />
				<xsl:call-template name="SummaryTests" />
				<xsl:call-template name="SummaryMedicalHistory" />
				<xsl:call-template name="SummaryDrugHistory" />
				<xsl:call-template name="SummaryParentMedicalHistory" />
				<xsl:call-template name="SummaryParentDrugHistory" />
				<xsl:call-template name="SummaryReactionEvent" />
				<xsl:call-template name="SummaryDrug" />
				<xsl:call-template name="SummaryActiveIngredient" />
				<xsl:call-template name="SummaryIndication" />
				<xsl:call-template name="SummaryDrugAdditional" />
				<xsl:call-template name="SummaryReporterComments" />				
				<xsl:call-template name="SummarySendersDiagnosis" />
				<xsl:call-template name="SummarySenderComments" />
			</narrativeincludeclinical>
			<reportercomment>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$SourceReporter and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">500</xsl:with-param>
				</xsl:call-template>
			</reportercomment>
			<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Diagnosis and hl7:code/@codeSystem=$oidObservationCode and hl7:author/hl7:assignedEntity/hl7:code/@code=$Sender and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]" mode="sender-diagnosis"/>
			<sendercomment>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$Sender and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">2000</xsl:with-param>
				</xsl:call-template>
			</sendercomment>
		</summary>
	</xsl:template>
	
	<!-- B.5.3. Sender’s diagnosis -->
	<xsl:template match="hl7:observationEvent" mode="sender-diagnosis">
		<!-- take only first occurrence -->
		<xsl:if test="position()=1" >
			<senderdiagnosismeddraversion><xsl:value-of select="hl7:value/@codeSystemVersion"/></senderdiagnosismeddraversion>
			<senderdiagnosis>
				<xsl:value-of select="hl7:value/@code"/>
				<xsl:value-of select="hl7:value/hl7:originalText"/>
			</senderdiagnosis>
		</xsl:if>
	</xsl:template>
			
	<!--	Additional information to case summary coming from the downgrade rules	-->
	
	<!-- CASE SUMMARY -->
	<xsl:template name="CaseSummary">
		<xsl:for-each select="hl7:component/hl7:observationEvent[hl7:code/@code=$SummaryAndComment and hl7:code/@codeSystem=$oidObservationCode and hl7:author/hl7:assignedEntity/hl7:code/@code=$Reporter and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]">
			<xsl:text>
CASE SUMMARY: (</xsl:text>
			<xsl:value-of select="hl7:value/@language"></xsl:value-of>
			<xsl:text>) </xsl:text><xsl:value-of select="hl7:value"></xsl:value-of>		
		</xsl:for-each>
	</xsl:template>
	
	<!-- ADDITIONAL DOCUMENTS-->
	<xsl:template name="SummaryAdditionalDocuments">
		<xsl:call-template name="DocumentList">
			<xsl:with-param name="NarrativeText" >
ADDITIONAL DOCUMENTS: </xsl:with-param>
			<xsl:with-param name="Length">100</xsl:with-param>
		</xsl:call-template>
	</xsl:template>
	
	<!-- DUPLICATE REPORTS -->
	<xsl:template name="SummaryDuplicateReports">
		<xsl:call-template name="ReportDuplicate">
			<xsl:with-param name="NarrativeText" >
CASE IDENTIFIER: </xsl:with-param>
			<xsl:with-param name="Length">50</xsl:with-param>
		</xsl:call-template>
	</xsl:template>	
	
	<!-- NULLIFICATION/AMENDMENT-->
	<xsl:template name="SummaryReportNullification">
		<xsl:if test="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$NullificationAmendmentCode]/hl7:value/@code = 2">
			<xsl:text>
NULLIFICATION/AMENDMENT: Amendment : </xsl:text>
			<xsl:value-of select="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$NullificationAmendmentReason]/hl7:value/hl7:originalText" />
		</xsl:if>
	</xsl:template>
	
	<!-- NULLIFICATION/AMENDMENT REASON-->
	<xsl:template name="SummaryReportNullificationReason">
		<xsl:variable name="reason" select="hl7:subjectOf2/hl7:investigationCharacteristic[hl7:code/@code=$NullificationAmendmentReason]/hl7:value/hl7:originalText"/>
		<xsl:if test="string-length($reason) > 200">
			<xsl:text>
NULLIFICATION/AMENDMENT REASON: </xsl:text><xsl:value-of select="$reason"/>
		</xsl:if>
	</xsl:template>
	
	<!-- STUDY NAME - SPONSOR STUDY NUMBER-->
	<xsl:template match="hl7:researchStudy" mode="SummaryStudyIdentification">
		<xsl:call-template name="StudyName">
			<xsl:with-param name="NarrativeText" >
STUDY NAME: </xsl:with-param>
			<xsl:with-param name="Length">100</xsl:with-param>
		</xsl:call-template>
		<xsl:if test="string-length(hl7:id/@extension)>35">
			<xsl:text>
SPONSOR STUDY NUMBER: </xsl:text>
			<xsl:value-of select="hl7:id/@extension"/>
		</xsl:if>
	</xsl:template>
	
	<!-- RESULTS OF TESTS -->
	<xsl:template name="SummaryTests">
		<xsl:variable name="resultsTests">
			<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$TestsAndProceduresRelevantToTheInvestigation]/hl7:component/hl7:observation" mode="results-tests-procedures"/>
		</xsl:variable>
		<xsl:if test="string-length($resultsTests) > 2000">
			<xsl:text>
TEST RESULTS: </xsl:text><xsl:value-of select="$resultsTests"/>
		</xsl:if>
	</xsl:template>
	
	<!-- MEDICAL HISTORY-->
	<xsl:template name="SummaryMedicalHistory">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions]/hl7:component/hl7:observation">
				<xsl:if test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment]/hl7:value)>100">
					<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment]/hl7:value"/>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="hl7:code/@code"/>
					<xsl:text>)</xsl:text>
					<xsl:if test="position() != last()">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)> 0">
			<xsl:text>
MEDICAL HISTORY: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- DRUG HISTORY-->
	<xsl:template name="SummaryDrugHistory">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugHistory]/hl7:component/hl7:substanceAdministration">
				<xsl:variable name="patientDrugName">
					<xsl:call-template name="DrugName" />
				</xsl:variable>
				<xsl:if test="string-length($patientDrugName)>100">
					<xsl:value-of select="$patientDrugName"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
DRUG HISTORY: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
		<!-- PARENT MEDICAL HISTORY-->
	<xsl:template name="SummaryParentMedicalHistory">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:player1/hl7:role[hl7:code/@code=$Parent]/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$RelevantMedicalHistoryAndConcurrentConditions]/hl7:component/hl7:observation">
				<xsl:if test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment]/hl7:value)>100">
					<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Comment]/hl7:value"/>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="hl7:code/@code"/>
					<xsl:text>)</xsl:text>
					<xsl:if test="position() != last()">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)> 0">
			<xsl:text>
PARENT MEDICAL HISTORY: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- PARENT DRUG HISTORY-->
	<xsl:template name="SummaryParentDrugHistory">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:player1/hl7:role[hl7:code/@code=$Parent]/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugHistory]/hl7:component/hl7:substanceAdministration">
				<xsl:variable name="parentDrugName">
					<xsl:call-template name="DrugName" />
				</xsl:variable>
				<xsl:if test="string-length($parentDrugName)>100">
					<xsl:value-of select="$parentDrugName"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
PARENT DRUG HISTORY: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- REACTION/EVENT-->
	<xsl:template name="SummaryReactionEvent">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction]" >
				<xsl:if test="string-length(hl7:value/hl7:originalText) > 200 and string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$ReactionForTranslation]/hl7:value) = 0">
					<xsl:value-of select="hl7:value/hl7:originalText"/><xsl:text> (</xsl:text><xsl:value-of select="hl7:value/hl7:originalText/@language"/><xsl:text>)</xsl:text>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
				<xsl:if test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$ReactionForTranslation]/hl7:value) > 200">
					<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$ReactionForTranslation]/hl7:value"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
REACTION/EVENT: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- DRUG-->
	<xsl:template name="SummaryDrug">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component/hl7:substanceAdministration/hl7:consumable/hl7:instanceOfKind">
				<xsl:variable name="medicinalProduct">
					<xsl:call-template name="MedicinalProduct" />
				</xsl:variable>
				<xsl:if test="string-length($medicinalProduct)>70">
					<xsl:value-of select="$medicinalProduct"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
DRUG: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- ACTIVE INGREDIENT-->
	<xsl:template name="SummaryActiveIngredient">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component/hl7:substanceAdministration/hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient/hl7:ingredientSubstance" >
				<xsl:variable name="activeIngredient">
					<xsl:call-template name="ActiveIngredient" />
				</xsl:variable>
				<xsl:if test="string-length($activeIngredient)>100">
					<xsl:value-of select="$activeIngredient"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
ACTIVE INGREDIENT: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- INDICATION-->
	<xsl:template name="SummaryIndication">
		
<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component">
	<xsl:for-each select="./hl7:substanceAdministration/hl7:inboundRelationship[@typeCode='RSON']/hl7:observation[hl7:performer/hl7:assignedEntity/hl7:code/@code=$SourceReporter and hl7:performer/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]" >
				<xsl:if test="not (position()=1)">
					<xsl:text>
	INDICATION </xsl:text>
					<xsl:value-of select="../../hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:name" />
					<xsl:text>: </xsl:text>
					<xsl:value-of select="hl7:value/@code" /> (<xsl:value-of select="hl7:value/@codeSystemVersion"/>)<xsl:text> </xsl:text><xsl:value-of select="hl7:value/hl7:originalText"/>
				</xsl:if>
		</xsl:for-each>
		</xsl:for-each>
	</xsl:template>
	
	<!-- DRUG ADDITIONAL-->
	<xsl:template name="SummaryDrugAdditional">
		<xsl:variable name="ContentString">
			<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component/hl7:substanceAdministration">
				<xsl:variable name="drugAdditional">(<xsl:value-of select="hl7:id/@extension"/> - <xsl:for-each select="hl7:consumable/hl7:instanceOfKind"><xsl:call-template name="MedicinalProduct"/></xsl:for-each>): <xsl:apply-templates select="." mode="drug-additional"><xsl:with-param name="DrugId" select="hl7:id/@extension"/></xsl:apply-templates></xsl:variable>
				<xsl:if test="string-length($drugAdditional)>1000">
					<xsl:value-of select="$drugAdditional"/>
					<xsl:if test="not (position()=last())">
						<xsl:text>; </xsl:text>
					</xsl:if>
				</xsl:if>
			</xsl:for-each>
		</xsl:variable>
		<xsl:if test="string-length($ContentString)>1">
			<xsl:text>
ADDITIONAL INFORMATION ON DRUG: </xsl:text>
			<xsl:value-of select="$ContentString"/>
		</xsl:if>
	</xsl:template>
	
	<!-- REPORTER COMMENTS -->
	<xsl:template name="SummaryReporterComments">
		<xsl:if test="string-length(hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$SourceReporter and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]/hl7:value)>500">
			<xsl:text>
REPORTER COMMENTS: </xsl:text>
			<xsl:value-of select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$SourceReporter and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]/hl7:value"/>
		</xsl:if>
	</xsl:template>
	
	<!-- ADDITIONAL SENDER'S DIAGNOSIS -->
	<xsl:template name="SummarySendersDiagnosis">
		<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Diagnosis and hl7:code/@codeSystem=$oidObservationCode and hl7:author/hl7:assignedEntity/hl7:code/@code=$Sender and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]/hl7:value" >
			<xsl:if test="not (position()=1)">
				<xsl:text>
ADDITIONAL SENDER'S DIAGNOSIS: </xsl:text><xsl:value-of select="@code"/><xsl:text> </xsl:text>(<xsl:value-of select="@codeSystemVersion"/>)
			</xsl:if>
		</xsl:for-each>
	</xsl:template>
	
		<!-- SENDER COMMENTS -->
	<xsl:template name="SummarySenderComments">
		<xsl:if test="string-length(hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$Sender and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]/hl7:value)>2000">
			<xsl:text>
SENDER COMMENTS: </xsl:text>
			<xsl:value-of select="hl7:component/hl7:adverseEventAssessment/hl7:component1/hl7:observationEvent[hl7:code/@code=$Comment and hl7:author/hl7:assignedEntity/hl7:code/@code=$Sender and hl7:author/hl7:assignedEntity/hl7:code/@codeSystem=$oidAssignedEntityRoleCode]/hl7:value"/>
		</xsl:if>
	</xsl:template>			
			
</xsl:stylesheet>
