#!/usr/bin/env python3
"""
Comprehensive GDPR Anonymizer: CLASSLA + Presidio + Regional Patterns

This script provides a unified solution that combines:
1. CLASSLA NER for natural language entities
2. Microsoft Presidio patterns for structured data
3. Regional patterns for Slovenian-specific data (tax numbers, etc.)
4. Advanced validation and GDPR compliance
"""

import classla
import re
import json
import phonenumbers
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class ComprehensiveGDPRAnonymizer:
    """
    Comprehensive GDPR-compliant anonymizer combining CLASSLA NER + Presidio patterns + regional data.
    """
    
    def __init__(self, language: str = 'sl', use_gpu: bool = False):
        """
        Initialize the comprehensive GDPR anonymizer.
        
        Args:
            language (str): Language code ('sl', 'hr', 'sr', 'bg', 'mk')
            use_gpu (bool): Whether to use GPU acceleration
        """
        self.language = language
        self.nlp = None
        self._setup_classla(use_gpu)
        self._setup_presidio_patterns()
        self._setup_regional_patterns()
    
    def _setup_classla(self, use_gpu: bool):
        """Setup CLASSLA pipeline with NER processor."""
        try:
            classla.download(self.language)
            self.nlp = classla.Pipeline(
                lang=self.language,
                use_gpu=use_gpu,
                processors='tokenize,pos,lemma,ner'
            )
            print(f"✓ CLASSLA pipeline ready for {self.language}")
        except Exception as e:
            print(f"✗ Error setting up CLASSLA: {e}")
            raise
    
    def _setup_presidio_patterns(self):
        """Setup regex patterns from Microsoft Presidio."""
        
        # Credit Card Patterns (from Presidio)
        self.credit_card_patterns = [
            # All Credit Cards (with Luhn validation)
            r"\b(?!1\d{12}(?!\d))((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b",
            # Visa
            r"\b4[0-9]{12}(?:[0-9]{3})?\b",
            # MasterCard
            r"\b5[1-5][0-9]{14}\b",
            # American Express
            r"\b3[47][0-9]{13}\b",
            # Discover
            r"\b6(?:011|5[0-9]{2})[0-9]{12}\b"
        ]
        
        # Email Patterns (from Presidio)
        self.email_patterns = [
            # Comprehensive Email Pattern
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b",
            # Simple Email Pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ]
        
        # Phone Number Patterns (basic patterns for initial detection)
        # We'll use Google's phonenumbers library for validation
        self.phone_patterns = [
            # Basic patterns to find potential phone numbers
            r"\b\+?[\d\s\-\(\)\.]{7,20}\b",
            # Common formats
            r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # US format
            r"\b\d{2}[-.\s]?\d{3}[-.\s]?\d{3,4}\b",  # European format
        ]
        
        # IP Address Patterns (from Presidio)
        self.ip_patterns = [
            # IPv4
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            # IPv6
            r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
        ]
        
        # Date Patterns (from Presidio + regional)
        self.date_patterns = [
            # Multiple Date Formats
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY or DD/MM/YYYY
            r"\b\d{4}-\d{2}-\d{2}\b",              # YYYY-MM-DD
            r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",        # DD.MM.YYYY
            # Regional formats
            r"\b\d{1,2}\.\s+\w+\s+\d{4}\b",        # DD. Month YYYY
            r"\b\d{1,2}-\d{1,2}-\d{4}\b"           # DD-MM-YYYY
        ]
        
        # URL Patterns (from Presidio)
        self.url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'ftp://[^\s]+'
        ]
        
        # IBAN Patterns (from Presidio)
        self.iban_patterns = [
            r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b'
        ]
    
    def _setup_regional_patterns(self):
        """Setup regional patterns for specific countries."""
        
        # Personal ID Patterns (regional)
        self.id_patterns = {
            'sl': [r'\b\d{13}\b'],  # Slovenian EMŠO
            'hr': [r'\b\d{11}\b'],  # Croatian OIB
            'sr': [r'\b\d{13}\b'],  # Serbian JMBG
            'bg': [r'\b\d{10}\b'],  # Bulgarian EGN
        }
        
        # Tax Number Patterns (regional)
        self.tax_patterns = {
            'sl': [
                # Slovenian Tax Number (Davčna številka) - 8 digits
                r'\b\d{8}\b',
                # Slovenian VAT Number (ID za DDV) - SI + 8 digits
                r'\bSI\d{8}\b',
                # Slovenian Company Registration Number (Matična številka) - 8 digits
                r'\b\d{8}\b'
            ],
            'hr': [
                # Croatian Tax Number (OIB) - 11 digits
                r'\b\d{11}\b',
                # Croatian VAT Number - HR + 11 digits
                r'\bHR\d{11}\b'
            ],
            'sr': [
                # Serbian Tax Number (PIB) - 9 digits
                r'\b\d{9}\b',
                # Serbian VAT Number - RS + 9 digits
                r'\bRS\d{9}\b'
            ],
            'bg': [
                # Bulgarian Tax Number (ЕГН) - 10 digits
                r'\b\d{10}\b',
                # Bulgarian VAT Number - BG + 9-10 digits
                r'\bBG\d{9,10}\b'
            ]
        }
        
        # Address Patterns (regional)
        self.address_patterns = {
            'sl': [
                # Slovenian postal code + city
                r'\b\d{4}\s+[A-ZČŠŽĆĐŠŽĆĐ][a-zčšžćđšžćđ\s]+\b',
                # Slovenian street + number
                r'\b[A-ZČŠŽĆĐŠŽĆĐ][a-zčšžćđšžćđ\s]+\s+\d{1,3}[a-z]?\b'
            ],
            'hr': [
                # Croatian postal code + city
                r'\b\d{5}\s+[A-ZČŠŽĆĐŠŽĆĐ][a-zčšžćđšžćđ\s]+\b'
            ],
            'sr': [
                # Serbian postal code + city
                r'\b\d{5}\s+[A-ZČŠŽĆĐŠŽĆĐ][a-zčšžćđšžćđ\s]+\b'
            ],
            'bg': [
                # Bulgarian postal code + city
                r'\b\d{4}\s+[A-ZČŠŽĆĐŠŽĆĐ][a-zčšžćđšžćđ\s]+\b'
            ]
        }
        
        # Bank Account Patterns (regional)
        self.bank_account_patterns = {
            'sl': [
                # Slovenian bank account (TRR) - 19 digits
                r'\b\d{3}-\d{2}-\d{13}\b',
                # Slovenian bank account (TRR) - 19 digits without dashes
                r'\b\d{19}\b'
            ],
            'hr': [
                # Croatian bank account (IBAN)
                r'\bHR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d\b'
            ],
            'sr': [
                # Serbian bank account (IBAN)
                r'\bRS\d{2}\s?\d{3}\s?\d{13}\s?\d{2}\b'
            ],
            'bg': [
                # Bulgarian bank account (IBAN)
                r'\bBG\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\b'
            ]
        }
    
    def extract_ner_entities(self, text: str) -> List[Dict]:
        """Extract named entities using CLASSLA NER."""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for sentence in doc.sentences:
            for token in sentence.tokens:
                if hasattr(token, 'ner') and token.ner != 'O':
                    entity_type = token.ner[2:] if token.ner.startswith(('B-', 'I-')) else token.ner
                    entities.append({
                        'text': token.text,
                        'type': entity_type,
                        'ner_tag': token.ner,
                        'start': token.start_char,
                        'end': token.end_char,
                        'detection_method': 'classla_ner',
                        'confidence': 'high'
                    })
        
        return entities
    
    def extract_presidio_entities(self, text: str) -> List[Dict]:
        """Extract entities using Presidio patterns."""
        entities = []
        
        # Extract credit cards
        for pattern in self.credit_card_patterns:
            for match in re.finditer(pattern, text):
                if self._validate_credit_card(match.group()):
                    entities.append({
                        'text': match.group(),
                        'type': 'CREDIT_CARD',
                        'start': match.start(),
                        'end': match.end(),
                        'detection_method': 'presidio_pattern',
                        'confidence': 'high'
                    })
        
        # Extract emails
        for pattern in self.email_patterns:
            for match in re.finditer(pattern, text):
                if self._validate_email(match.group()):
                    entities.append({
                        'text': match.group(),
                        'type': 'EMAIL',
                        'start': match.start(),
                        'end': match.end(),
                        'detection_method': 'presidio_pattern',
                        'confidence': 'high'
                    })
        
        # Extract phone numbers using Google's phonenumbers library
        phone_entities = self._extract_phone_numbers_with_google(text)
        entities.extend(phone_entities)
        
        # Extract IP addresses
        for pattern in self.ip_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'IP_ADDRESS',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'presidio_pattern',
                    'confidence': 'high'
                })
        
        # Extract dates
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'DATE',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'presidio_pattern',
                    'confidence': 'medium'
                })
        
        # Extract URLs
        for pattern in self.url_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'URL',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'presidio_pattern',
                    'confidence': 'high'
                })
        
        # Extract IBAN
        for pattern in self.iban_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'IBAN',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'presidio_pattern',
                    'confidence': 'high'
                })
        
        return entities
    
    def extract_regional_entities(self, text: str) -> List[Dict]:
        """Extract regional entities specific to the language."""
        entities = []
        
        # Extract personal IDs
        id_patterns = self.id_patterns.get(self.language, [])
        for pattern in id_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'PERSONAL_ID',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'regional_pattern',
                    'confidence': 'high'
                })
        
        # Extract tax numbers
        tax_patterns = self.tax_patterns.get(self.language, [])
        for pattern in tax_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'TAX_NUMBER',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'regional_pattern',
                    'confidence': 'high'
                })
        
        # Extract bank accounts
        bank_patterns = self.bank_account_patterns.get(self.language, [])
        for pattern in bank_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'BANK_ACCOUNT',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'regional_pattern',
                    'confidence': 'high'
                })
        
        # Extract addresses
        address_patterns = self.address_patterns.get(self.language, [])
        for pattern in address_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'ADDRESS',
                    'start': match.start(),
                    'end': match.end(),
                    'detection_method': 'regional_pattern',
                    'confidence': 'medium'
                })
        
        return entities
    
    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm (from Presidio)."""
        # Remove spaces and dashes
        sanitized = re.sub(r'[-\s]', '', card_number)
        
        if not sanitized.isdigit():
            return False
        
        # Luhn algorithm
        def digits_of(n: str) -> List[int]:
            return [int(dig) for dig in str(n)]
        
        digits = digits_of(sanitized)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        
        return checksum % 10 == 0
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address (basic validation)."""
        # Basic email validation
        if '@' not in email or '.' not in email:
            return False
        
        # Check for valid TLD
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        domain = parts[1]
        if '.' not in domain:
            return False
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number (basic validation)."""
        # Remove common separators
        sanitized = re.sub(r'[-\s\(\)]', '', phone)
        
        # Check if it's a reasonable length
        if len(sanitized) < 7 or len(sanitized) > 15:
            return False
        
        # Check if it contains only digits and +
        if not re.match(r'^\+?[\d]+$', sanitized):
            return False
        
        return True
    
    def _extract_phone_numbers_with_google(self, text: str) -> List[Dict]:
        """
        Extract phone numbers using Google's phonenumbers library.
        
        Args:
            text (str): Input text to search for phone numbers
            
        Returns:
            List[Dict]: List of phone number entities
        """
        entities = []
        
        # Try different regions for phone number detection
        regions = ['SI', 'HR', 'RS', 'BG', 'US', 'GB', 'DE', 'FR']  # Add more as needed
        
        for region in regions:
            try:
                # Find all phone numbers in the text
                matcher = phonenumbers.PhoneNumberMatcher(text, region)
                for match in matcher:
                    try:
                        # Parse the phone number
                        phone_number = phonenumbers.parse(match.raw_string, region)
                        
                        # Validate the phone number
                        if phonenumbers.is_valid_number(phone_number):
                            # Get formatted number
                            formatted_number = phonenumbers.format_number(
                                phone_number, 
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL
                            )
                            
                            # Get region info
                            number_region = phonenumbers.region_code_for_number(phone_number)
                            
                            entities.append({
                                'text': match.raw_string,
                                'type': 'PHONE',
                                'start': match.start,
                                'end': match.end,
                                'detection_method': 'google_phonenumbers',
                                'confidence': 'high',
                                'metadata': {
                                    'formatted_number': formatted_number,
                                    'region': number_region,
                                    'number_type': phonenumbers.number_type(phone_number),
                                    'is_valid': True
                                }
                            })
                    except phonenumbers.NumberParseException:
                        # Skip invalid numbers
                        continue
                        
            except Exception as e:
                # Skip regions that cause issues
                continue
        
        # Remove duplicates (same phone number detected multiple times)
        unique_entities = []
        seen_numbers = set()
        
        for entity in entities:
            # Normalize phone number for comparison
            normalized = re.sub(r'[\s\-\(\)\.]', '', entity['text'])
            if normalized not in seen_numbers:
                seen_numbers.add(normalized)
                unique_entities.append(entity)
        
        return unique_entities
    
    def anonymize_text(self, text: str, mask_char: str = '*', 
                      preserve_types: List[str] = None, use_descriptive_masks: bool = False) -> Dict:
        """
        Anonymize text using CLASSLA NER + Presidio patterns + Regional patterns.
        
        Args:
            text (str): Input text to anonymize
            mask_char (str): Character to use for masking (ignored if use_descriptive_masks=True)
            preserve_types (List[str]): Entity types to preserve (not mask)
            use_descriptive_masks (bool): If True, use descriptive tags like <MASKED_EMAIL> instead of asterisks
            
        Returns:
            Dict: Anonymization results
        """
        if preserve_types is None:
            preserve_types = []
        
        # Extract all entities from all sources
        ner_entities = self.extract_ner_entities(text)
        presidio_entities = self.extract_presidio_entities(text)
        regional_entities = self.extract_regional_entities(text)
        
        # Combine all entities
        all_entities = ner_entities + presidio_entities + regional_entities
        
        # Remove duplicates (entities that overlap)
        filtered_entities = self._remove_overlapping_entities(all_entities)
        
        # Filter out preserved types
        entities_to_mask = [
            entity for entity in filtered_entities
            if entity['type'] not in preserve_types
        ]
        
        # Sort by start position (descending) to avoid index issues
        entities_to_mask.sort(key=lambda x: x['start'], reverse=True)
        
        # Create masked text
        masked_text = text
        masked_entities = []
        
        for entity in entities_to_mask:
            start = entity['start']
            end = entity['end']
            original_text = entity['text']
            
            # Create mask based on preference
            if use_descriptive_masks:
                mask = f"<MASKED_{entity['type'].upper()}>"
            else:
                mask = mask_char * (end - start)
            
            masked_text = masked_text[:start] + mask + masked_text[end:]
            
            masked_entities.append({
                'original': original_text,
                'type': entity['type'],
                'mask': mask,
                'position': (start, end),
                'detection_method': entity['detection_method'],
                'confidence': entity['confidence']
            })
        
        # Assess privacy risk
        privacy_risk = self._assess_privacy_risk(masked_entities)
        
        return {
            'original_text': text,
            'anonymized_text': masked_text,
            'masked_entities': masked_entities,
            'total_entities_masked': len(masked_entities),
            'privacy_risk': privacy_risk,
            'gdpr_compliance': self._check_gdpr_compliance(masked_entities),
            'detection_methods': {
                'classla_ner': len([e for e in masked_entities if e['detection_method'] == 'classla_ner']),
                'presidio_patterns': len([e for e in masked_entities if e['detection_method'] == 'presidio_pattern']),
                'google_phonenumbers': len([e for e in masked_entities if e['detection_method'] == 'google_phonenumbers']),
                'regional_patterns': len([e for e in masked_entities if e['detection_method'] == 'regional_pattern'])
            }
        }
    
    def _remove_overlapping_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove overlapping entities, keeping the longer ones."""
        if not entities:
            return entities
        
        # Sort by length (descending) and start position
        entities.sort(key=lambda x: (x['end'] - x['start'], -x['start']), reverse=True)
        
        filtered = []
        for entity in entities:
            # Check if this entity overlaps with any already filtered entity
            overlaps = False
            for filtered_entity in filtered:
                if (entity['start'] < filtered_entity['end'] and 
                    entity['end'] > filtered_entity['start']):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered
    
    def _assess_privacy_risk(self, masked_entities: List[Dict]) -> str:
        """Assess privacy risk based on masked entities."""
        if not masked_entities:
            return 'low'
        
        # Count different entity types
        entity_types = [entity['type'] for entity in masked_entities]
        
        # High-risk entities
        high_risk = ['PERSONAL_ID', 'CREDIT_CARD', 'EMAIL', 'IBAN', 'TAX_NUMBER', 'BANK_ACCOUNT']
        # Medium-risk entities
        medium_risk = ['PER', 'PHONE', 'IP_ADDRESS']
        # Low-risk entities
        low_risk = ['LOC', 'ORG', 'URL', 'DATE', 'ADDRESS']
        
        high_count = sum(1 for t in entity_types if t in high_risk)
        medium_count = sum(1 for t in entity_types if t in medium_risk)
        
        if high_count > 0:
            return 'high'
        elif medium_count > 1:
            return 'medium'
        else:
            return 'low'
    
    def _check_gdpr_compliance(self, masked_entities: List[Dict]) -> Dict:
        """Check GDPR compliance based on masked entities."""
        entity_types = [entity['type'] for entity in masked_entities]
        
        # GDPR Article 4 definitions
        personal_data_types = {
            'PER': 'Personal data (names, identifiers)',
            'EMAIL': 'Personal data (contact information)',
            'PHONE': 'Personal data (contact information)',
            'PERSONAL_ID': 'Special category data (national ID)',
            'CREDIT_CARD': 'Financial data',
            'IBAN': 'Financial data (bank account)',
            'TAX_NUMBER': 'Financial data (tax information)',
            'BANK_ACCOUNT': 'Financial data (bank account)',
            'IP_ADDRESS': 'Personal data (online identifier)',
            'DATE': 'Personal data (birth dates, etc.)',
            'LOC': 'Personal data (location)',
            'ORG': 'Personal data (affiliation)',
            'URL': 'Personal data (online activity)',
            'ADDRESS': 'Personal data (location)'
        }
        
        compliance_report = {
            'gdpr_article_4_compliant': True,
            'personal_data_detected': [],
            'special_categories': [],
            'recommendations': []
        }
        
        for entity_type in entity_types:
            if entity_type in personal_data_types:
                compliance_report['personal_data_detected'].append(
                    personal_data_types[entity_type]
                )
                
                if entity_type in ['PERSONAL_ID', 'CREDIT_CARD', 'IBAN', 'TAX_NUMBER', 'BANK_ACCOUNT']:
                    compliance_report['special_categories'].append(
                        f'{personal_data_types[entity_type]}'
                    )
        
        if compliance_report['personal_data_detected']:
            compliance_report['recommendations'].append(
                'Ensure proper legal basis for processing personal data'
            )
        
        if compliance_report['special_categories']:
            compliance_report['recommendations'].append(
                'Special category data detected - additional safeguards required'
            )
        
        return compliance_report


def main():
    """Demonstrate comprehensive GDPR-compliant anonymization."""
    
    print("Comprehensive GDPR Anonymizer (CLASSLA + Presidio + Regional Patterns)")
    print("=" * 80)
    
    # Initialize anonymizer
    try:
        anonymizer = ComprehensiveGDPRAnonymizer(language='sl')
    except Exception as e:
        print(f"Error initializing anonymizer: {e}")
        return
    
    # Test cases with various sensitive data including Slovenian-specific
    test_cases = [
        {
            'name': 'Slovenian Personal & Financial Information',
            'text': 'Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678, rojena 20.5.1980, EMŠO: 2005800500999, davčna številka: 12345678, TRR: 123-45-1234567890123'
        },
        {
            'name': 'International Phone Numbers',
            'text': 'Contact: +1 (555) 123-4567 (US), +44 20 7946 0958 (UK), +386 1 234 5678 (Slovenia), 031 123 456 (Slovenia mobile)'
        },
        {
            'name': 'Mixed Sensitive Data',
            'text': 'Janez Novak (janez.novak@email.com) živi v Ljubljani, telefon: 031 123 456, rojen 15.3.1985, kartica: 5555 5555 5555 4444, obiskal je https://www.banka.si'
        },
        {
            'name': 'Croatian Data Example',
            'text': 'Ana Horvat (ana@email.hr) iz Zagreba, tel: +385 1 234 5678, OIB: 12345678901, ID za PDV: HR12345678901'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Original: {test_case['text']}")
        
        # Anonymize
        result = anonymizer.anonymize_text(test_case['text'])
        
        print(f"Anonymized: {result['anonymized_text']}")
        print(f"Privacy Risk: {result['privacy_risk'].upper()}")
        print(f"Entities masked: {result['total_entities_masked']}")
        print(f"Detection methods: {result['detection_methods']}")
        
        # Show masked entities
        if result['masked_entities']:
            print("Masked entities:")
            for entity in result['masked_entities']:
                print(f"  - {entity['original']} ({entity['type']}) → {entity['mask']} [{entity['detection_method']}] ({entity['confidence']})")
        
        # Show GDPR compliance
        compliance = result['gdpr_compliance']
        print(f"GDPR Compliance: {compliance['gdpr_article_4_compliant']}")
        if compliance['recommendations']:
            print("Recommendations:")
            for rec in compliance['recommendations']:
                print(f"  - {rec}")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("Comprehensive Solution Summary")
    print("=" * 80)
    print("✅ This comprehensive anonymizer combines:")
    print("   - CLASSLA NER for natural language entities")
    print("   - Microsoft Presidio patterns for structured data")
    print("   - Google phonenumbers library for phone validation")
    print("   - Regional patterns for country-specific data")
    print("   - Advanced validation and GDPR compliance")
    print("\n🎯 Supported data types:")
    print("   - Persons, Locations, Organizations (CLASSLA)")
    print("   - Emails, Credit Cards, IPs, Dates, URLs (Presidio)")
    print("   - Phone Numbers (Google phonenumbers library)")
    print("   - Tax Numbers, Bank Accounts, Personal IDs (Regional)")
    print("   - Addresses (Regional patterns)")
    print("\n🌍 Regional support:")
    print("   - Slovenian: EMŠO, davčna številka, TRR, ID za DDV")
    print("   - Croatian: OIB, ID za PDV")
    print("   - Serbian: JMBG, PIB")
    print("   - Bulgarian: EGN, VAT numbers")


if __name__ == "__main__":
    main() 