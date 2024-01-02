<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - B.4 Part)
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
		Amendment:	Addition of conversions for EU specific data fields, fixes for Drug not administered, PIXcode and SUBs code excluded from appearing in drug name
		
		Version:		1.2
		Date:			30/03/2017
		Status:			Replaced
		Author:			Nick Halsey (EU)
		Amendment:	Correction to drugseparatedosagenumb {as neccessary} to  {asneccessary}
		
		Version:		1.3
		Date:			03/08/2017
		Status:			Current
		Author:			Nick Halsey (EU)
		Amendment:	Correction to handle UCUM dosage units that are not mapped to R2 codes
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif" exclude-result-prefixes="hl7 xsi xsl fo mif">
	<!--	B.4. Drug(s) Information	-->
	<xsl:template name="Drug">
		<xsl:for-each select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation and hl7:code/@codeSystem=$oidValueGroupingCode]/hl7:component/hl7:substanceAdministration">
			<xsl:choose>
				<!-- Drug with dosage -->
				<xsl:when test="count(hl7:outboundRelationship2[@typeCode='COMP'])>0">
					<xsl:for-each select="hl7:outboundRelationship2[@typeCode='COMP']">
						<xsl:apply-templates select=".." mode="drug-tag">
							<xsl:with-param name="DosageNum">
								<xsl:value-of select="position()"/>
							</xsl:with-param>
						</xsl:apply-templates>
					</xsl:for-each>
				</xsl:when>
				<!-- Drug without dosage -->
				<xsl:otherwise>
					<xsl:apply-templates select="." mode="drug-tag">
					</xsl:apply-templates>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>
	<xsl:template match="hl7:substanceAdministration" mode="drug-tag">
		<xsl:param name="DosageNum">0</xsl:param>
		<xsl:variable name="DrugId" select="hl7:id/@root"/>
		<drug>
			<!-- B.4.k.1. Characterization of drug role -->
			<xsl:choose>
				<xsl:when test="../../../../../../hl7:component/hl7:causalityAssessment[hl7:code/@code=$InterventionCharacterization and hl7:code/@codeSystem=$oidObservationCode and hl7:subject2/hl7:productUseReference/hl7:id/@root=$DrugId]/hl7:value/@code != 4">
					<drugcharacterization>
						<xsl:value-of select="../../../../../../hl7:component/hl7:causalityAssessment[hl7:code/@code=$InterventionCharacterization and hl7:code/@codeSystem=$oidObservationCode and hl7:subject2/hl7:productUseReference/hl7:id/@root=$DrugId]/hl7:value/@code"/>
					</drugcharacterization>
				</xsl:when>
				<xsl:otherwise>
					<drugcharacterization>1</drugcharacterization>
				</xsl:otherwise>
			</xsl:choose>
			<!-- B.4.k.2.0; B.4.k.2.1; B.4.k.2.2; B.4.k.2.4 -->
			<xsl:apply-templates select="hl7:consumable/hl7:instanceOfKind" mode="drug-manufactured-product"/>
			<!-- B.4.k.4.r.9 Batch/lot number -->
			<xsl:for-each select="hl7:outboundRelationship2/hl7:substanceAdministration">
				<xsl:if test="position() = $DosageNum">
					<xsl:apply-templates select="." mode="drug-batch-number"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.3 Holder and authorization/application number of drug -->
			<xsl:apply-templates select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:asManufacturedProduct" mode="drug-holder"/>
			<!-- B.4.k.4.r1 - 5 Dosage Information -->
			<xsl:for-each select="hl7:outboundRelationship2/hl7:substanceAdministration">
				<xsl:if test="position() = $DosageNum">
					<xsl:apply-templates select="." mode="drug-dosage-information1"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.5 cumulative dose to the reaction/event -->
			<xsl:apply-templates select="hl7:outboundRelationship2[@typeCode='SUMM']/hl7:observation[hl7:code/@code=$CumulativeDoseToReaction and hl7:code/@codeSystem=$oidObservationCode]" mode="drug-cumulative-dosage"/>
			<!-- B.4.k.4.r.10 - 13 Dosage Information -->
			<xsl:for-each select="hl7:outboundRelationship2/hl7:substanceAdministration">
				<xsl:if test="position() = $DosageNum">
					<xsl:apply-templates select="." mode="drug-dosage-information2"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.6 Gestation period at time of exposure -->
			<xsl:apply-templates select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$GestationPeriod]" mode="reaction-gestation-period"/>
			<!-- B.4.k.7.r.1 Indication for use in the case from primary source -->
			<xsl:for-each select="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$Indication and hl7:performer/hl7:assignedEntity/hl7:code/@code=$SourceReporter]">
				<xsl:if test="position()=1">
					<xsl:apply-templates select="." mode="drug-indication"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.4.r.6 Date of start of drug -->
			<xsl:for-each select="hl7:outboundRelationship2[@typeCode='COMP']/hl7:substanceAdministration">
				<xsl:if test="position() = $DosageNum">
					<xsl:apply-templates select="." mode="drug-start-date"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.9.r.3.1; B.4.k.9.r.3.2 - Time interval between beginning  of drug administration and start/end of reaction/event -->
			<xsl:for-each select="hl7:outboundRelationship1[@typeCode='SAS']">
				<xsl:if test="position()=1">
					<xsl:call-template name="drug-period-sas"/>
				</xsl:if>
			</xsl:for-each>
			<xsl:for-each select="hl7:outboundRelationship1[@typeCode='SAE']">
				<xsl:if test="position()=1">
					<xsl:call-template name="drug-period-sae"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.4.r.7; B.4.k.4.r.8 - Date of last/ Duration of drug administration -->
			<xsl:for-each select="hl7:outboundRelationship2[@typeCode='COMP']/hl7:substanceAdministration">
				<xsl:if test="position() = $DosageNum">
					<xsl:apply-templates select="." mode="drug-end-date"/>
				</xsl:if>
			</xsl:for-each>
			<!-- B.4.k.8 Action(s) taken with drug -->
			<actiondrug>
				<xsl:choose>
					<xsl:when test="hl7:inboundRelationship/hl7:act/hl7:code/@code = 0">5</xsl:when>
					<xsl:when test="hl7:inboundRelationship/hl7:act/hl7:code/@code = 9">6</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="hl7:inboundRelationship/hl7:act/hl7:code/@code"/>
					</xsl:otherwise>
				</xsl:choose>
			</actiondrug>
			<!-- B.4.k.9 Recurrance of reaction -->
			<drugrecurreadministration>
				<xsl:choose>
					<xsl:when test="count(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$RecurranceOfReaction and hl7:code/@codeSystem=$oidObservationCode and hl7:value/@code = 1]) > 0">
						<xsl:text>1</xsl:text>
					</xsl:when>
					<xsl:when test="count(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$RecurranceOfReaction and hl7:code/@codeSystem=$oidObservationCode and hl7:value/@code = 2]) > 0">
						<xsl:text>2</xsl:text>
					</xsl:when>
					<xsl:when test="count(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$RecurranceOfReaction and hl7:code/@codeSystem=$oidObservationCode and hl7:value/@code > 2]) > 0">
						<xsl:text>3</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text/>
					</xsl:otherwise>
				</xsl:choose>
			</drugrecurreadministration>
			<!-- B.4.k.10 Additional information on drug -->
			<drugadditional>
				<xsl:variable name="drug-additional">
					<xsl:apply-templates select="." mode="drug-additional">
						<xsl:with-param name="DrugId" select="$DrugId"/>
					</xsl:apply-templates>
				</xsl:variable>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:value-of select="$drug-additional"/>
					</xsl:with-param>
					<xsl:with-param name="string-length">1000</xsl:with-param>
				</xsl:call-template>
			</drugadditional>
			<!-- B.4.k.2.3.r.1 Active Ingredient name -->
			<xsl:apply-templates select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient/hl7:ingredientSubstance" mode="active-substance-name"/>
			<!-- B.4.k.9.r.4 Did reaction recur on readministration? -->
			<xsl:apply-templates select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$RecurranceOfReaction and hl7:code/@codeSystem=$oidObservationCode]" mode="drug-recurrence"/>
			<!-- B.4.k.9.r.2.r Relatedness of drug to reaction(s)/event(s) -->
			<xsl:apply-templates select="../../../../../../hl7:component/hl7:causalityAssessment[hl7:code/@code = $Causality and hl7:subject2/hl7:productUseReference/hl7:id/@root = $DrugId]" mode="drug-reaction"/>
		</drug>
	</xsl:template>
	<!-- B.4.k.10 Additional information on drug -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-additional">
		<xsl:param name="DrugId"/>
		<xsl:apply-templates select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:ingredient" mode="drug-additional1"/>
		<xsl:variable name="AdditionalInfo">
			<xsl:if test="../../../../../../hl7:component/hl7:causalityAssessment[hl7:code/@code=$InterventionCharacterization and hl7:code/@codeSystem=$oidObservationCode and hl7:subject2/hl7:productUseReference/hl7:id/@root=$DrugId]/hl7:value/@code = 4">
				DRUG NOT ADMINISTERED
			</xsl:if>
			<xsl:if test="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Blinded and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@value = 'true'">
				<xsl:text>INVESTIGATIONAL</xsl:text>
				<xsl:if test="count(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CodedDrugInformation and hl7:code/@codeSystem=$oidObservationCode]) + count(hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$AdditionalInformation and hl7:code/@codeSystem=$oidObservationCode]) > 0">
					<xsl:text>, </xsl:text>
				</xsl:if>
			</xsl:if>
			<xsl:for-each select="hl7:outboundRelationship2/hl7:substanceAdministration/hl7:routeCode[@codeSystem != $oidICHRoute]">
				; ROUTE : <xsl:value-of select="@code"/>
				<xsl:if test="hl7:originalText"> [<xsl:value-of select="hl7:originalText"/>]</xsl:if>
				(<xsl:value-of select="@codeSystem"/> ; <xsl:value-of select="@codeSystemVersion"/>)
			</xsl:for-each>
			<xsl:for-each select="hl7:outboundRelationship2/hl7:substanceAdministration/hl7:inboundRelationship/hl7:observation[hl7:code/@code = $ParentRouteOfAdministration and hl7:code/@codeSystem=$oidObservationCode]/hl7:value[@codeSystem != $oidICHRoute]">
				; PARENT ROUTE : <xsl:value-of select="@code"/>
				<xsl:if test="hl7:originalText"> [<xsl:value-of select="hl7:originalText"/>]</xsl:if>
				(<xsl:value-of select="@codeSystem"/> ; <xsl:value-of select="@codeSystemVersion"/>)
			</xsl:for-each>
			<xsl:apply-templates select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$CodedDrugInformation and hl7:code/@codeSystem=$oidObservationCode]" mode="drug-additional2"/>
			<xsl:apply-templates select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$AdditionalInformation and hl7:code/@codeSystem=$oidObservationCode]" mode="drug-additional3"/>
		</xsl:variable>
		<xsl:variable name="AdditionalInfo2">
			<xsl:apply-templates select="hl7:outboundRelationship2/hl7:substanceAdministration/hl7:consumable/hl7:instanceOfKind/hl7:productInstanceInstance/hl7:part/hl7:partDeviceInstance" mode="drug-device"/>
		</xsl:variable>
		<xsl:if test="string-length($AdditionalInfo) > 0 or string-length($AdditionalInfo2) >0">
			<xsl:text>Additional info: </xsl:text>
			<xsl:value-of select="$AdditionalInfo"/>
			<xsl:value-of select="$AdditionalInfo2"/>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.2.0; B.4.k.2.1; B.4.k.2.2; B.4.k.2.4 -->
	<xsl:template match="hl7:instanceOfKind" mode="drug-manufactured-product">
		<medicinalproduct>
			<xsl:variable name="medicinalProduct">
				<xsl:call-template name="MedicinalProduct"/>
			</xsl:variable>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string">
					<xsl:value-of select="$medicinalProduct"/>
				</xsl:with-param>
				<xsl:with-param name="string-length">70</xsl:with-param>
			</xsl:call-template>
		</medicinalproduct>
		<obtaindrugcountry>
			<xsl:value-of select="hl7:subjectOf/hl7:productEvent[hl7:code/@code=$RetailSupply and hl7:code/@codeSystem=$oidActionPerformedCode]/hl7:performer/hl7:assignedEntity/hl7:representedOrganization/hl7:addr/hl7:country"/>
		</obtaindrugcountry>
	</xsl:template>
	<!-- B.4.k.4.r.9 Batch/lot number -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-batch-number">
		<drugbatchnumb>
			<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:productInstanceInstance/hl7:lotNumberText"/>
		</drugbatchnumb>
	</xsl:template>
	<!-- B.4.k.3 Holder and authorization/application number of drug -->
	<xsl:template match="hl7:asManufacturedProduct" mode="drug-holder">
		<drugauthorizationnumb>
			<xsl:value-of select="hl7:subjectOf/hl7:approval/hl7:id/@extension"/>
		</drugauthorizationnumb>
		<drugauthorizationcountry>
			<xsl:value-of select="hl7:subjectOf/hl7:approval/hl7:author/hl7:territorialAuthority/hl7:territory/hl7:code/@code"/>
		</drugauthorizationcountry>
		<drugauthorizationholder>
			<xsl:value-of select="hl7:subjectOf/hl7:approval/hl7:holder/hl7:role/hl7:playingOrganization/hl7:name"/>
		</drugauthorizationholder>
	</xsl:template>
	<!-- B.4.k.2.2 Medicinal product name as reported by the primary source -->
	<xsl:template name="MedicinalProduct">
		<xsl:if test="hl7:kindOfProduct/hl7:code/@codeSystem=$MPID">
			<xsl:text>MPID: </xsl:text>
		</xsl:if>
		<xsl:if test="hl7:kindOfProduct/hl7:code/@codeSystem=$PhPID">
			<xsl:text>PhPID: </xsl:text>
		</xsl:if>
		<xsl:if test="string-length(hl7:kindOfProduct/hl7:code/@code) > 0 and hl7:kindOfProduct/hl7:code/@codeSystem !='PIX-code' ">
			<xsl:value-of select="hl7:kindOfProduct/hl7:code/@code"/>
			<xsl:text> (</xsl:text>
			<xsl:value-of select="hl7:kindOfProduct/hl7:code/@codeSystemVersion"/>
			<xsl:text>): </xsl:text>
		</xsl:if>
		<xsl:if test="$XEVMPD =1">
			<xsl:choose>
				<xsl:when test="string-length(hl7:kindOfProduct/hl7:code/@displayName) > 0 and string-length(hl7:kindOfProduct/hl7:code/@code) > 0 and hl7:kindOfProduct/hl7:code/@codeSystem ='PIX-code'">
					<xsl:value-of select="hl7:kindOfProduct/hl7:code/@displayName"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="hl7:kindOfProduct/hl7:name"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
		<xsl:if test="$XEVMPD !=1">
			<xsl:value-of select="hl7:kindOfProduct/hl7:name"/>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.2.3.r.1 Active Ingredient name -->
	<xsl:template match="hl7:ingredientSubstance" mode="active-substance-name">
		<xsl:variable name="activeIngredient">
			<xsl:call-template name="ActiveIngredient"/>
		</xsl:variable>
		<xsl:if test="string-length($activeIngredient) > 0">
			<activesubstance>
				<activesubstancename>
					<xsl:call-template name="truncate">
						<xsl:with-param name="string">
							<xsl:value-of select="$activeIngredient"/>
						</xsl:with-param>
						<xsl:with-param name="string-length">100</xsl:with-param>
					</xsl:call-template>
				</activesubstancename>
			</activesubstance>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.2.3.r.1 Active Ingredient name -->
	<xsl:template name="ActiveIngredient">
		<xsl:if test="@classCode='MMAT'">
			<xsl:if test="string-length(hl7:code/@code) > 0 and hl7:code/@codeSystem !='SUB-code'">
				<xsl:text>TERMID: </xsl:text>
				<xsl:value-of select="hl7:code/@code"/>
				<xsl:text> (</xsl:text>
				<xsl:value-of select="hl7:code/@codeSystemVersion"/>
				<xsl:text>): </xsl:text>
			</xsl:if>
			<xsl:if test="$XEVMPD=1">
				<xsl:choose>
					<xsl:when test="string-length(hl7:code/@displayName) > 0 and string-length(hl7:code/@code) > 0 and hl7:code/@codeSystem ='SUB-code'">
						<xsl:value-of select="hl7:code/@displayName"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="hl7:name"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:if>
			<xsl:if test="$XEVMPD!=1">
				<xsl:value-of select="hl7:name"/>
			</xsl:if>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.4.r1 - 5 Dosage Information -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-dosage-information1">
		<xsl:variable name="DoseUnit" select="hl7:doseQuantity/@unit"/>
		<xsl:choose>
			<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type='UCUM']/code[./@r3 =$DoseUnit]) > 0">
				<!--UCUM mapped to R2 code list-->
				<drugstructuredosagenumb>
					<xsl:value-of select="hl7:doseQuantity/@value"/>
				</drugstructuredosagenumb>
				<drugstructuredosageunit>
					<xsl:call-template name="getMapping">
						<xsl:with-param name="type">UCUM</xsl:with-param>
						<xsl:with-param name="code" select="hl7:doseQuantity/@unit"/>
					</xsl:call-template>
				</drugstructuredosageunit>
				<drugseparatedosagenumb/>
			</xsl:when>
			<xsl:otherwise>
				<!--UCUM not mapped to R2 code list-->
				<drugstructuredosagenumb/>
				<drugstructuredosageunit/>
				<drugseparatedosagenumb/>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="hl7:effectiveTime//hl7:period/@unit = '{cyclical}' or hl7:effectiveTime//hl7:period/@unit = '{asnecessary}' or hl7:effectiveTime//hl7:period/@unit = '{total}'">
				<drugintervaldosageunitnumb>
					<xsl:value-of select="hl7:effectiveTime//hl7:period/@value"/>
				</drugintervaldosageunitnumb>
				<drugintervaldosagedefinition>
					<xsl:call-template name="getMapping">
						<xsl:with-param name="type">UCUM</xsl:with-param>
						<xsl:with-param name="code" select="hl7:effectiveTime//hl7:period/@unit"/>
					</xsl:call-template>
				</drugintervaldosagedefinition>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="string-length(hl7:effectiveTime//hl7:period/@value) &lt; 4 and not(contains(hl7:effectiveTime//hl7:period/@unit, '{'))">
					<drugintervaldosageunitnumb>
						<xsl:value-of select="hl7:effectiveTime//hl7:period/@value"/>
					</drugintervaldosageunitnumb>
					<drugintervaldosagedefinition>
						<xsl:call-template name="getMapping">
							<xsl:with-param name="type">UCUM</xsl:with-param>
							<xsl:with-param name="code" select="hl7:effectiveTime//hl7:period/@unit"/>
						</xsl:call-template>
					</drugintervaldosagedefinition>
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- B.4.k.5 cumulative dose to the reaction/event -->
	<xsl:template match="hl7:observation" mode="drug-cumulative-dosage">
		<drugcumulativedosagenumb>
			<xsl:value-of select="hl7:value/@value"/>
		</drugcumulativedosagenumb>
		<drugcumulativedosageunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="hl7:value/@unit"/>
			</xsl:call-template>
		</drugcumulativedosageunit>
	</xsl:template>
	<!-- B.4.k.4.r.10 - 13 Dosage Information -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-dosage-information2">
		<drugdosagetext>
			<xsl:call-template name="truncate">
				<xsl:with-param name="string">
					<!-- Dosage text -->
					<xsl:value-of select="hl7:text"/>
					<xsl:variable name="DoseUnit" select="hl7:doseQuantity/@unit"/>
					<xsl:choose>
						<xsl:when test="count(document('mapping-codes.xml')/mapping-codes/mapping-code[./@type='UCUM']/code[./@r3 =$DoseUnit]) = 0">
							<xsl:text> (</xsl:text>
							<xsl:value-of select="hl7:doseQuantity/@value"/>
							<xsl:value-of select="hl7:doseQuantity/@unit"/>
							<xsl:text>)</xsl:text>
						</xsl:when>
					</xsl:choose>
					<!-- Case of time interval of 4N -->
					<xsl:if test="string-length(hl7:effectiveTime//hl7:period/@value) > 3">
						<xsl:if test="string-length(hl7:text) > 0">
							<xsl:text> ; </xsl:text>
						</xsl:if>Time Interval: <xsl:value-of select="hl7:effectiveTime/hl7:comp/hl7:period/@value"/>
						<xsl:text> </xsl:text>
						<xsl:value-of select="hl7:effectiveTime/hl7:comp/hl7:period/@unit"/>
					</xsl:if>
					<!-- Case of CYCLICAL dosage -->
					<xsl:if test="hl7:effectiveTime//hl7:period/@unit = '{cyclical}'">
						<xsl:if test="string-length(hl7:text) > 0">
							<xsl:text> ; </xsl:text>
						</xsl:if>CYCLICAL
					</xsl:if>
					<!-- Case of AS NECESSARY dosage -->
					<xsl:if test="hl7:effectiveTime//hl7:period/@unit = '{asnecessary}'">
						<xsl:if test="string-length(hl7:text) > 0">
							<xsl:text> ; </xsl:text>
						</xsl:if>AS NECESSARY
					</xsl:if>
					<!-- Case of TOTAL dosage -->
					<xsl:if test="hl7:effectiveTime//hl7:period/@unit = '{total}'">
						<xsl:if test="string-length(hl7:text) > 0">
							<xsl:text> ; </xsl:text>
						</xsl:if>IN TOTAL
					</xsl:if>
				</xsl:with-param>
				<xsl:with-param name="string-length">100</xsl:with-param>
			</xsl:call-template>
		</drugdosagetext>
		<drugdosageform>
			<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:formCode/hl7:originalText"/>
			<xsl:if test="string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:formCode/hl7:originalText) = 0 and string-length(hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:formCode/@code) > 0">
				<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:formCode/@code"/> (<xsl:value-of select="hl7:consumable/hl7:instanceOfKind/hl7:kindOfProduct/hl7:formCode/@codeSystemVersion"/>)</xsl:if>
		</drugdosageform>
		<xsl:if test="string-length(hl7:routeCode/@code) + string-length(hl7:routeCode/originalText) > 0">
			<drugadministrationroute>
				<xsl:choose>
					<xsl:when test="hl7:routeCode/@codeSystem = $oidICHRoute">
						<xsl:value-of select="hl7:routeCode/@code"/>
					</xsl:when>
					<xsl:otherwise>050</xsl:otherwise>
				</xsl:choose>
			</drugadministrationroute>
		</xsl:if>
		<xsl:if test="string-length(hl7:inboundRelationship/hl7:observation[hl7:code/@code=$ParentRouteOfAdministration and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code) + string-length(hl7:inboundRelationship/hl7:observation[hl7:code/@code=$ParentRouteOfAdministration and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/orignalText) > 0">
			<drugparadministration>
				<xsl:choose>
					<xsl:when test="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$ParentRouteOfAdministration and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@codeSystem = $oidICHRoute">
						<xsl:value-of select="hl7:inboundRelationship/hl7:observation[hl7:code/@code=$ParentRouteOfAdministration and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
					</xsl:when>
					<xsl:otherwise>050</xsl:otherwise>
				</xsl:choose>
			</drugparadministration>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.6 Gestation period at time of exposure -->
	<xsl:template match="hl7:observation" mode="reaction-gestation-period">
		<reactiongestationperiod>
			<xsl:choose>
				<xsl:when test="hl7:value/@xsi:type = 'PQ'">
					<xsl:value-of select="hl7:value/@value"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="hl7:value/@code"/>
				</xsl:otherwise>
			</xsl:choose>
		</reactiongestationperiod>
		<reactiongestationperiodunit>
			<xsl:choose>
				<xsl:when test="hl7:value/@xsi:type = 'PQ'">
					<xsl:call-template name="getMapping">
						<xsl:with-param name="type">UCUM</xsl:with-param>
						<xsl:with-param name="code" select="hl7:value/@unit"/>
					</xsl:call-template>
				</xsl:when>
			</xsl:choose>
		</reactiongestationperiodunit>
	</xsl:template>
	<!-- B.4.k.7.r.1 Indication for use in the case from primary source -->
	<xsl:template match="hl7:observation" mode="drug-indication">
		<drugindicationmeddraversion>
			<xsl:value-of select="hl7:value/@codeSystemVersion"/>
		</drugindicationmeddraversion>
		<drugindication>
			<xsl:value-of select="hl7:value/@code"/>
		</drugindication>
	</xsl:template>
	<!-- B.4.k.4.r.6 Date of start of drug -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-start-date">
		<xsl:if test="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:low/@value">
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">drugstartdate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:low/@value"/>
				<xsl:with-param name="min-format">CCYY</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.9.r.3.1 - Time interval between beginning  of drug administration and start of reaction/event -->
	<xsl:template name="drug-period-sas">
		<drugstartperiod>
			<xsl:value-of select="hl7:pauseQuantity/@value"/>
		</drugstartperiod>
		<drugstartperiodunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="hl7:pauseQuantity/@unit"/>
			</xsl:call-template>
		</drugstartperiodunit>
	</xsl:template>
	<!-- B.4.k.9.r.3.2 - Time interval between beginning  of drug administration and end of reaction/event -->
	<xsl:template name="drug-period-sae">
		<druglastperiod>
			<xsl:value-of select="hl7:pauseQuantity/@value"/>
		</druglastperiod>
		<druglastperiodunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="hl7:pauseQuantity/@unit"/>
			</xsl:call-template>
		</druglastperiodunit>
	</xsl:template>
	<!-- B.4.k.4.r.7; B.4.k.4.r.8 - Date of last/ Duration of drug administration -->
	<xsl:template match="hl7:substanceAdministration" mode="drug-end-date">
		<xsl:if test="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:high/@value">
			<xsl:call-template name="convertDate">
				<xsl:with-param name="elementName">drugenddate</xsl:with-param>
				<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:high/@value"/>
				<xsl:with-param name="min-format">CCYY</xsl:with-param>
				<xsl:with-param name="max-format">CCYYMMDD</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		<xsl:if test="count(hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:width)>0">
			<drugtreatmentduration>
				<xsl:value-of select="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:width/@value"/>
			</drugtreatmentduration>
			<drugtreatmentdurationunit>
				<xsl:call-template name="getMapping">
					<xsl:with-param name="type">UCUM</xsl:with-param>
					<xsl:with-param name="code" select="hl7:effectiveTime/hl7:comp[@xsi:type='IVL_TS']/hl7:width/@unit"/>
				</xsl:call-template>
			</drugtreatmentdurationunit>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.19. Additional information on drug - Part 1 -->
	<xsl:template match="hl7:ingredient" mode="drug-additional1">
		<xsl:choose>
			<xsl:when test="@classCode='ACTI'">
				<xsl:if test="string-length(hl7:quantity/hl7:numerator/@value) > 0">
					<xsl:text>Ingredient (</xsl:text>
					<xsl:value-of select="hl7:ingredientSubstance/hl7:name"/>
					<xsl:text>): </xsl:text>
					<xsl:value-of select="hl7:quantity/hl7:numerator/@value"/>
					<xsl:value-of select="hl7:quantity/hl7:numerator/@unit"/>
					<xsl:if test="hl7:quantity/hl7:denominator/@value and hl7:quantity/hl7:denominator/@value != 1">
						<xsl:text> / </xsl:text>
						<xsl:value-of select="hl7:quantity/hl7:denominator/@value"/>
						<xsl:if test="hl7:quantity/hl7:denominator/@unit">
							<xsl:value-of select="hl7:quantity/hl7:denominator/@unit"/>
						</xsl:if>
					</xsl:if>
					<xsl:text>; </xsl:text>
				</xsl:if>
			</xsl:when>
		</xsl:choose>
	</xsl:template>
	<!-- B.4.k.19. Additional information on drug - Part 2 -->
	<xsl:template match="hl7:observation" mode="drug-additional2">
		<xsl:call-template name="getText">
			<xsl:with-param name="id">
				<xsl:value-of select="hl7:value/@code"/>
			</xsl:with-param>
		</xsl:call-template>
		<xsl:value-of select="hl7:value/hl7:originalText"/>
		<xsl:if test="not (position()=last())">
			<xsl:text>, </xsl:text>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.19. Additional information on drug - Part 3 -->
	<xsl:template match="hl7:observation" mode="drug-additional3">
		<xsl:value-of select="hl7:value"/>
		<xsl:if test="not (position()=last())">
			<xsl:text>, </xsl:text>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.9.r.4 Did reaction recur on readministration? -->
	<xsl:template match="hl7:observation" mode="drug-recurrence">
		<xsl:if test="hl7:value/@code = 1">
			<xsl:variable name="DrugRecurationId" select="hl7:outboundRelationship1/hl7:actReference/hl7:id/@root"/>
			<drugrecurrence>
				<drugrecuractionmeddraversion>
					<xsl:value-of select="../../../../../../hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$DrugRecurationId]/hl7:value/@codeSystemVersion"/>
				</drugrecuractionmeddraversion>
				<drugrecuraction>
					<xsl:value-of select="../../../../../../hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$DrugRecurationId]/hl7:value/@code"/>
				</drugrecuraction>
			</drugrecurrence>
		</xsl:if>
	</xsl:template>
	<!-- B.4.k.9.r.2.r Relatedness of drug to reaction(s)/event(s) -->
	<xsl:template match="hl7:causalityAssessment" mode="drug-reaction">
		<xsl:variable name="ReactionId" select="hl7:subject1/hl7:adverseEffectReference/hl7:id/@root"/>
		<!-- EU causality assessment in not final development-->
		<xsl:choose>
			<xsl:when test="hl7:methodCode/@codeSystem='2.16.840.1.113883.3.989.5.1.1.5.2'">
				<drugreactionrelatedness>
					<drugreactionassesmeddraversion>
						<xsl:value-of select="../../hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$ReactionId]/hl7:value/@codeSystemVersion"/>
					</drugreactionassesmeddraversion>
					<drugreactionasses>
						<xsl:value-of select="../../hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$ReactionId]/hl7:value/@code"/>
					</drugreactionasses>
					<drugassessmentsource>
						<xsl:value-of select="hl7:author/hl7:assignedEntity/hl7:code/@code"/>
					</drugassessmentsource>
					<xsl:choose>
						<xsl:when test="hl7:author/hl7:assignedEntity/hl7:code/@code > 3">
							<drugassessmentmethod>EVCTMR3</drugassessmentmethod>
						</xsl:when>
						<xsl:otherwise>
							<drugassessmentmethod>EVCTM</drugassessmentmethod>
						</xsl:otherwise>
					</xsl:choose>
					<drugresult>
						<xsl:value-of select="hl7:value/@code"/>
					</drugresult>
				</drugreactionrelatedness>
			</xsl:when>
			<xsl:otherwise>
				<!-- ICH causality assessment as in original ICH document-->
				<drugreactionrelatedness>
					<drugreactionassesmeddraversion>
						<xsl:value-of select="../../hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$ReactionId]/hl7:value/@codeSystemVersion"/>
					</drugreactionassesmeddraversion>
					<drugreactionasses>
						<xsl:value-of select="../../hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction and hl7:id/@root=$ReactionId]/hl7:value/@code"/>
					</drugreactionasses>
					<drugassessmentsource>
						<xsl:value-of select="hl7:author/hl7:assignedEntity/hl7:code/hl7:originalText"/>
					</drugassessmentsource>
					<drugassessmentmethod>
						<xsl:call-template name="truncate">
							<xsl:with-param name="string">
								<xsl:value-of select="hl7:methodCode/hl7:originalText"/>
							</xsl:with-param>
							<xsl:with-param name="string-length">35</xsl:with-param>
						</xsl:call-template>
					</drugassessmentmethod>
					<drugresult>
						<xsl:call-template name="truncate">
							<xsl:with-param name="string">
								<xsl:value-of select="hl7:value"/>
							</xsl:with-param>
							<xsl:with-param name="string-length">35</xsl:with-param>
						</xsl:call-template>
					</drugresult>
				</drugreactionrelatedness>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- B.4.k.19. Additional information on drug - Part 4 -Device components -->
	<xsl:template match="hl7:partDeviceInstance" mode="drug-device">
		<xsl:text>Device: </xsl:text>
		<xsl:value-of select="hl7:asInstanceOfKind/hl7:kindOfMaterialKind/hl7:name"/>
		<xsl:if test="string-length(hl7:asInstanceOfKind/hl7:kindOfMaterialKind/hl7:code/@code) > 0">
			<xsl:text> (</xsl:text>
			<xsl:value-of select="hl7:asInstanceOfKind/hl7:kindOfMaterialKind/hl7:code/@code"/>
			<xsl:text>, </xsl:text>
			<xsl:value-of select="hl7:asInstanceOfKind/hl7:kindOfMaterialKind/hl7:code/@codeSystem"/>
			<xsl:text>, </xsl:text>
			<xsl:value-of select="hl7:asInstanceOfKind/hl7:kindOfMaterialKind/hl7:code/@codeSystemVersion"/>
		</xsl:if>
		<xsl:if test="string-length(hl7:lotNumberText) > 0">
			<xsl:text>) Device lot: </xsl:text>
			<xsl:value-of select="hl7:lotNumberText"/>
		</xsl:if>
		<xsl:text> </xsl:text>
	</xsl:template>
</xsl:stylesheet>
